import httpx
import logging
from config import OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)

GIPHY_API_KEY = None


async def search_gif(query: str, limit: int = 5) -> str:
    """
    Busca GIFs no Giphy.
    Usa API pública se GIPHY_API_KEY não estiver configurada (limitado).
    """
    global GIPHY_API_KEY
    if GIPHY_API_KEY is None:
        from config import GIPHY_API_KEY

        GIPHY_API_KEY = GIPHY_API_KEY

    try:
        if GIPHY_API_KEY:
            url = "https://api.giphy.com/v1/gifs/search"
            params = {
                "api_key": GIPHY_API_KEY,
                "q": query,
                "limit": limit,
                "rating": "g",
            }
        else:
            url = "https://api.giphy.com/v1/gifs/search"
            params = {
                "api_key": "dc6zaTOxFJmzC",
                "q": query,
                "limit": limit,
                "rating": "g",
            }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=OLLAMA_TIMEOUT)

            if response.status_code != 200:
                return f"❌ Erro ao buscar GIFs: {response.status_code}"

            data = response.json()
            gifs = data.get("data", [])

            if not gifs:
                return "Nenhum GIF encontrado para essa busca."

            results = []
            for gif in gifs[:limit]:
                title = gif.get("title", "GIF")
                url = gif.get("images", {}).get("original", {}).get("url", "")
                preview = gif.get("images", {}).get("fixed_height", {}).get("url", "")
                results.append(f"*{title}*\n{preview if preview else url}")

            return "🎬 GIFs encontrados:\n\n" + "\n\n".join(results)
    except httpx.TimeoutException:
        return "⏳ Timeout ao buscar GIFs"
    except Exception as e:
        logger.error(f"Erro no search_gif: {e}")
        return f"❌ Erro: {str(e)}"
