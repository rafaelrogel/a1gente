import httpx
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import OLLAMA_URL, MODEL_NAME, OLLAMA_NUM_CTX, OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)


async def call_ollama(
    messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    url = f"{OLLAMA_URL}/api/chat"
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {"num_ctx": OLLAMA_NUM_CTX},
    }
    if tools:
        payload["tools"] = tools

    async with httpx.AsyncClient() as client:
        try:
            start_time = datetime.now()
            response = await client.post(url, json=payload, timeout=OLLAMA_TIMEOUT)
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Ollama respondeu em {duration:.2f}s")

            if response.status_code != 200:
                return {
                    "message": {
                        "role": "assistant",
                        "content": f"⚠️ *Erro Ollama ({response.status_code})*: {response.text}",
                    }
                }
            return response.json()
        except httpx.TimeoutException:
            return {
                "message": {
                    "role": "assistant",
                    "content": f"⏳ *Erro de Timeout*: O Ollama demorou mais de {OLLAMA_TIMEOUT}s para responder. O contexto pode ser grande demais ou o VPS está sobrecarregado.",
                }
            }
        except (httpx.ConnectError, httpx.ConnectTimeout):
            return {
                "message": {
                    "role": "assistant",
                    "content": f"❌ *Erro de Conexão*: Não foi possível conectar ao Ollama em {OLLAMA_URL}. Verifique se o serviço está rodando.",
                }
            }
        except Exception as e:
            logger.error(f"Erro inesperado no call_ollama: {repr(e)}")
            return {
                "message": {
                    "role": "assistant",
                    "content": f"❗ *Erro Inesperado*: {repr(e)}",
                }
            }
