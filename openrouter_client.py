import httpx
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def call_openrouter(
    messages: List[Dict[str, Any]],
    tools: Optional[List[Dict[str, Any]]] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    if not OPENROUTER_API_KEY:
        return {
            "message": {
                "role": "assistant",
                "content": "⚠️ OPENROUTER_API_KEY não configurado. Configure no .env",
            }
        }

    if model is None:
        model = OPENROUTER_MODEL

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://nordic-claw.online",
        "X-Title": "Nordic Claw Agent",
    }

    payload = {
        "model": model,
        "messages": messages,
    }

    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    async with httpx.AsyncClient() as client:
        try:
            start_time = datetime.now()
            response = await client.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
                timeout=120.0,
            )
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"OpenRouter ({model}) respondeu em {duration:.2f}s")

            if response.status_code != 200:
                error_text = response.text
                logger.error(f"OpenRouter error {response.status_code}: {error_text}")
                return {
                    "message": {
                        "role": "assistant",
                        "content": f"⚠️ Erro OpenRouter ({response.status_code}): {error_text[:200]}",
                    }
                }

            data = response.json()

            if "choices" not in data or len(data["choices"]) == 0:
                return {
                    "message": {
                        "role": "assistant",
                        "content": "⚠️ OpenRouter não retornou resposta válida",
                    }
                }

            choice = data["choices"][0]
            message = choice.get("message", {})

            result = {"message": message}

            if message.get("tool_calls"):
                result["message"]["tool_calls"] = message["tool_calls"]

            return result

        except httpx.TimeoutException:
            return {
                "message": {
                    "role": "assistant",
                    "content": "⏳ OpenRouter timeout (>120s)",
                }
            }
        except httpx.ConnectError as e:
            return {
                "message": {
                    "role": "assistant",
                    "content": f"❌ Erro de conexão OpenRouter: {str(e)}",
                }
            }
        except Exception as e:
            logger.error(f"Erro inesperado OpenRouter: {repr(e)}")
            return {
                "message": {
                    "role": "assistant",
                    "content": f"❗ Erro OpenRouter: {repr(e)}",
                }
            }


async def list_openrouter_models() -> str:
    if not OPENROUTER_API_KEY:
        return "⚠️ OPENROUTER_API_KEY não configurado"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://openrouter.ai/api/v1/models",
                headers=headers,
                timeout=30.0,
            )

            if response.status_code != 200:
                return f"❌ Erro {response.status_code}: {response.text[:100]}"

            data = response.json()
            models = data.get("data", [])

            free_models = [
                m["id"]
                for m in models
                if m.get("pricing", {}).get("prompt", "0") == "0"
                or "free" in m.get("id", "").lower()
            ]

            result = "📋 *Modelos Gratuitos OpenRouter:*\n\n"
            for m in sorted(free_models)[:20]:
                result += f"• `{m}`\n"

            result += f"\n🔄 *Modelo atual:* `{OPENROUTER_MODEL}`"
            return result

        except Exception as e:
            return f"❌ Erro ao listar modelos: {str(e)}"
