import httpx
import logging
from typing import Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def fetch_webpage(url: str) -> str:
    """Faz GET num site e retorna o texto limpo."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            soup = BeautifulSoup(response.text, "html.parser")
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text(separator=" ")
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = "\n".join(chunk for chunk in chunks if chunk)
            return clean_text[:2000]
    except Exception as e:
        return f"Erro ao acessar a URL {url}: {str(e)}"
