import httpx
import logging
import re
from datetime import datetime
from config import OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)


async def scrape_reddit(subreddit: str, sort: str = "hot", limit: int = 10) -> str:
    """
    Busca posts recentes de um subreddit do Reddit.

    Usa o Reddit JSON API (não requer autenticação para leitura básica).
    Alternativas: 'hot', 'new', 'top', 'rising'
    """
    try:
        sort_url = {
            "hot": ".json?limit=25",
            "new": "/new/.json?limit=25",
            "top": "/top/.json?limit=25",
            "rising": "/rising/.json?limit=25",
        }.get(sort.lower(), ".json?limit=25")

        url = f"https://www.reddit.com/r/{subreddit}{sort_url}"

        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; NordicClawBot/1.0; +https://github.com/rafaelrogel/a1gente)",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=OLLAMA_TIMEOUT)

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

            for i, post in enumerate(posts[:limit], 1):
                post_data = post.get("data", {})
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

                results.append(f"\n{i}. *{title}*")
                results.append(
                    f"   👤 @{author} | 👍 {score} | 💬 {num_comments} | {time_str}"
                )
                if selftext:
                    results.append(f"   📝 {selftext}...")
                results.append(f"   🔗 {url}")

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
