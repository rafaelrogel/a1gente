import httpx
import logging
from config import OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)

LANGUAGES = {
    "portuguese": "pt",
    "english": "en",
    "spanish": "es",
    "french": "fr",
    "german": "de",
    "italian": "it",
    "dutch": "nl",
    "russian": "ru",
    "chinese": "zh",
    "japanese": "ja",
    "korean": "ko",
    "arabic": "ar",
    "pt": "pt",
    "en": "en",
    "es": "es",
    "fr": "fr",
    "de": "de",
    "it": "it",
    "nl": "nl",
    "ru": "ru",
    "zh": "zh",
    "ja": "ja",
    "ko": "ko",
    "ar": "ar",
}


async def translate_text(text: str, target_lang: str = "english") -> str:
    """
    Translate text using MyMemory API (free, no API key required).
    Target language can be name (english) or code (en).
    """
    try:
        lang_code = LANGUAGES.get(target_lang.lower(), target_lang)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.mymemory.translated.net/get",
                params={"q": text, "langpair": f"en|{lang_code}"},
                timeout=OLLAMA_TIMEOUT,
            )

            if response.status_code != 200:
                return f"ERRO: Falha no serviço de tradução ({response.status_code})"

            data = response.json()

            if data.get("responseStatus") == 200:
                translated = data["responseData"]["translatedText"]
                return translated
            else:
                return f"ERRO: {data.get('responseDetails', 'Erro desconhecido')}"
    except httpx.TimeoutException:
        return f"ERRO: Timeout no serviço de tradução"
    except Exception as e:
        logger.error(f"Erro no translate_text: {e}")
        return f"ERRO: {str(e)}"
