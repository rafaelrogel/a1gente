import httpx
import logging
from datetime import datetime, timedelta
from config import OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)

GITHUB_TOKEN = None


async def get_github_activity(repo: str, days: int = 7) -> str:
    """
    Busca atividade recente de um repositório GitHub.
    Mostra PRs e issues recentes.
    """
    global GITHUB_TOKEN
    if GITHUB_TOKEN is None:
        from config import GITHUB_TOKEN

        GITHUB_TOKEN = GITHUB_TOKEN

    try:
        headers = {}
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"

        since_date = (datetime.now() - timedelta(days=days)).isoformat() + "Z"

        async with httpx.AsyncClient() as client:
            prs_response = await client.get(
                f"https://api.github.com/repos/{repo}/pulls",
                params={"state": "all", "since": since_date, "per_page": 10},
                headers=headers,
                timeout=OLLAMA_TIMEOUT,
            )

            issues_response = await client.get(
                f"https://api.github.com/repos/{repo}/issues",
                params={"since": since_date, "per_page": 10, "state": "all"},
                headers=headers,
                timeout=OLLAMA_TIMEOUT,
            )

            if prs_response.status_code == 404:
                return f"❌ Repositório '{repo}' não encontrado."
            if prs_response.status_code == 403:
                return f"⚠️ Rate limit atingido. Tente novamente mais tarde."

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
                for pr in open_prs[:5]:
                    title = pr.get("title", "")[:60]
                    author = pr.get("user", {}).get("login", "unknown")
                    url = pr.get("html_url", "")
                    output.append(f"• {title}\n  @{author} | {url}")

            merged_prs = [
                pr for pr in prs if pr.get("state") == "closed" and pr.get("merged_at")
            ]
            if merged_prs:
                output.append(f"\n✅ *{len(merged_prs)} PR(s) mesclada(s):*")
                for pr in merged_prs[:5]:
                    title = pr.get("title", "")[:60]
                    author = pr.get("user", {}).get("login", "unknown")
                    url = pr.get("html_url", "")
                    output.append(f"• {title}\n  @{author} | {url}")

            recent_issues = [
                iss
                for iss in issues
                if not iss.get("pull_request")
                and iss.get("created_at", "") > since_date
            ]
            if recent_issues:
                output.append(f"\n🆕 *{len(recent_issues)} issue(s) aberta(s):*")
                for iss in recent_issues[:5]:
                    title = iss.get("title", "")[:60]
                    author = iss.get("user", {}).get("login", "unknown")
                    url = iss.get("html_url", "")
                    output.append(f"• {title}\n  @{author} | {url}")

            if len(output) == 1:
                return f"📊 *{repo}*\n\nNenhuma atividade encontrada nos últimos {days} dias."

            return "\n".join(output)
    except httpx.TimeoutException:
        return "⏳ Timeout ao acessar GitHub"
    except Exception as e:
        logger.error(f"Erro no get_github_activity: {e}")
        return f"❌ Erro: {str(e)}"
