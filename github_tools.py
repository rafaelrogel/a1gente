import httpx
import logging
from datetime import datetime, timedelta
from config import OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)

GITHUB_TOKEN = None
MAX_TITLE_LENGTH = 60
MAX_BODY_LENGTH = 500
MAX_OUTPUT_LENGTH = 2000


def _get_github_token():
    """Get GitHub token from config, logging warning if not set."""
    global GITHUB_TOKEN
    if GITHUB_TOKEN is None:
        from config import GITHUB_TOKEN as token

        GITHUB_TOKEN = token

    if not GITHUB_TOKEN:
        logger.warning("⚠️ GITHUB_TOKEN não definido. Limite de rate pode ser atingido.")

    return GITHUB_TOKEN


def _truncate(text: str, max_len: int) -> str:
    """Truncate text to max length."""
    if not text:
        return ""
    return text[:max_len] + "..." if len(text) > max_len else text


async def get_github_activity(repo: str, days: int = 7) -> str:
    """
    Busca atividade recente de um repositório GitHub.
    Mostra PRs e issues recentes.
    """
    try:
        # Clamp days to valid range
        days = max(1, min(30, days))

        token = _get_github_token()

        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"token {token}"

        since_date = (datetime.now() - timedelta(days=days)).isoformat() + "Z"

        async with httpx.AsyncClient() as client:
            prs_response = await client.get(
                f"https://api.github.com/repos/{repo}/pulls",
                params={"state": "all", "per_page": 10},
                headers=headers,
                timeout=OLLAMA_TIMEOUT,
            )

            # Check rate limit before second request
            if prs_response.status_code == 403:
                return (
                    "⚠️ GitHub rate limit atingido. Tente novamente em alguns minutos."
                )

            if prs_response.status_code == 404:
                return f"⚠️ Repositório não encontrado: {repo}"

            issues_response = await client.get(
                f"https://api.github.com/repos/{repo}/issues",
                params={"since": since_date, "per_page": 10, "state": "all"},
                headers=headers,
                timeout=OLLAMA_TIMEOUT,
            )

            if issues_response.status_code == 403:
                return (
                    "⚠️ GitHub rate limit atingido. Tente novamente em alguns minutos."
                )

            prs = prs_response.json() if prs_response.status_code == 200 else []
            issues = (
                issues_response.json() if issues_response.status_code == 200 else []
            )

            output = [f"📊 *Atividade GitHub: {repo}*\n(últimos {days} dias)\n"]

            open_prs = [
                pr for pr in prs if pr.get("state") == "open" and not pr.get("draft")
            ]
            if open_prs:
                output.append(f"\n🔶 *{len(open_prs)} PR(s) aberta(s):*")
                for pr in open_prs[:10]:
                    title = _truncate(pr.get("title", ""), MAX_TITLE_LENGTH)
                    author = pr.get("user", {}).get("login", "unknown")
                    url = pr.get("html_url", "")
                    body = _truncate(pr.get("body", ""), MAX_BODY_LENGTH)
                    output.append(f"• {title}\n  @{author} | {url}")
                    if body:
                        output.append(f"  {body}")

            merged_prs = [
                pr for pr in prs if pr.get("state") == "closed" and pr.get("merged_at")
            ]
            if merged_prs:
                output.append(f"\n✅ *{len(merged_prs)} PR(s) mesclada(s):*")
                for pr in merged_prs[:10]:
                    title = _truncate(pr.get("title", ""), MAX_TITLE_LENGTH)
                    author = pr.get("user", {}).get("login", "unknown")
                    url = pr.get("html_url", "")
                    body = _truncate(pr.get("body", ""), MAX_BODY_LENGTH)
                    output.append(f"• {title}\n  @{author} | {url}")
                    if body:
                        output.append(f"  {body}")

            recent_issues = [
                iss
                for iss in issues
                if not iss.get("pull_request")
                and iss.get("created_at", "") > since_date
            ]
            if recent_issues:
                output.append(f"\n🆕 *{len(recent_issues)} issue(s) aberta(s):*")
                for iss in recent_issues[:10]:
                    title = _truncate(iss.get("title", ""), MAX_TITLE_LENGTH)
                    author = iss.get("user", {}).get("login", "unknown")
                    url = iss.get("html_url", "")
                    body = _truncate(iss.get("body", ""), MAX_BODY_LENGTH)
                    output.append(f"• {title}\n  @{author} | {url}")
                    if body:
                        output.append(f"  {body}")

            if len(output) == 1:
                return f"📊 *{repo}*\n\nNenhuma atividade encontrada nos últimos {days} dias."

            result = "\n".join(output)
            return (
                result[:MAX_OUTPUT_LENGTH] + "..."
                if len(result) > MAX_OUTPUT_LENGTH
                else result
            )

    except httpx.TimeoutException:
        return "⏳ Timeout ao acessar GitHub"
    except httpx.ConnectError:
        return "⚠️ Não foi possível conectar ao GitHub. Verifique sua conexão."
    except Exception as e:
        logger.error(f"Erro no get_github_activity: {e}")
        return f"❌ Erro: {str(e)}"
