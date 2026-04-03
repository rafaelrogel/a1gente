import httpx
import logging
import re
from datetime import datetime
from config import OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)


async def scrape_reddit(subreddit: str, sort: str = "hot", limit: int = 10) -> str:
    """
    Busca posts recentes de um subreddit do Reddit.

    Usa a API de busca com filtro de subreddit (workaround para limitacoes da API).
    Alternativas de sort: 'hot', 'new', 'top', 'rising'
    """
    try:
        sort_param = {"hot": "hot", "new": "new", "top": "top", "rising": "rising"}.get(
            sort.lower(), "hot"
        )

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        async with httpx.AsyncClient() as client:
            url = "https://www.reddit.com/search.json"
            params = {
                "q": f"subreddit:{subreddit}",
                "limit": min(limit * 2, 25),
                "sort": sort_param,
            }

            response = await client.get(
                url, params=params, headers=headers, timeout=OLLAMA_TIMEOUT
            )

            if response.status_code == 404:
                return f"❌ Subreddit 'r/{subreddit}' não encontrado."
            if response.status_code == 429:
                return f"⚠️ Rate limit do Reddit atingido. Tente novamente em alguns minutos."
            if response.status_code != 200:
                return f"❌ Erro ao acessar Reddit: {response.status_code}"

            data = response.json()
            posts = data.get("data", {}).get("children", [])

            if not posts:
                return f"Nenhum post encontrado em r/{subreddit}."

            results = [f"📱 *r/{subreddit}* ({sort})*\n"]

            count = 0
            for post in posts:
                if count >= limit:
                    break
                post_data = post.get("data", {})
                post_subreddit = post_data.get("subreddit", "")
                if post_subreddit.lower() != subreddit.lower():
                    continue

                title = post_data.get("title", "")[:80]
                author = post_data.get("author", "[deleted]")
                score = post_data.get("score", 0)
                num_comments = post_data.get("num_comments", 0)
                created = post_data.get("created_utc", 0)
                permalink = post_data.get("permalink", "")
                url = f"https://reddit.com{permalink}"
                selftext = (
                    post_data.get("selftext", "")[:100]
                    if post_data.get("selftext")
                    else None
                )

                time_str = (
                    datetime.fromtimestamp(created).strftime("%d/%m %H:%M")
                    if created
                    else ""
                )

                count += 1
                results.append(f"\n{count}. *{title}*")
                results.append(
                    f"   👤 @{author} | 👍 {score} | 💬 {num_comments} | {time_str}"
                )
                if selftext:
                    results.append(f"   📝 {selftext}...")
                results.append(f"   🔗 {url}")

            if count == 0:
                return f"Nenhum post encontrado em r/{subreddit}."

            return "\n".join(results)
    except httpx.TimeoutException:
        return "⏳ Timeout ao acessar Reddit"
    except Exception as e:
        logger.error(f"Erro no scrape_reddit: {e}")
        return f"❌ Erro: {str(e)}"


async def search_reddit(query: str, limit: int = 10) -> str:
    """
    Busca posts em todos os subreddits usando a API de busca do Reddit.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; NordicClawBot/1.0; +https://github.com/rafaelrogel/a1gente)"
        }

        url = "https://www.reddit.com/search.json"
        params = {"q": query, "limit": limit, "sort": "relevance"}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, params=params, headers=headers, timeout=OLLAMA_TIMEOUT
            )

            if response.status_code == 429:
                return f"⚠️ Rate limit do Reddit atingido. Tente novamente mais tarde."
            if response.status_code != 200:
                return f"❌ Erro ao buscar no Reddit: {response.status_code}"

            data = response.json()
            posts = data.get("data", {}).get("children", [])

            if not posts:
                return f"Nenhum resultado para '{query}'."

            results = [f"🔍 *Resultados para '{query}'*\n"]

            for i, post in enumerate(posts[:limit], 1):
                post_data = post.get("data", {})
                title = post_data.get("title", "")[:80]
                subreddit = post_data.get("subreddit", "")
                author = post_data.get("author", "[deleted]")
                score = post_data.get("score", 0)
                permalink = post_data.get("permalink", "")
                url = f"https://reddit.com{permalink}"

                results.append(f"\n{i}. *{title}*")
                results.append(f"   📱 r/{subreddit} | 👤 @{author} | 👍 {score}")
                results.append(f"   🔗 {url}")

            return "\n".join(results)
    except httpx.TimeoutException:
        return "⏳ Timeout ao buscar no Reddit"
    except Exception as e:
        logger.error(f"Erro no search_reddit: {e}")
        return f"❌ Erro: {str(e)}"
