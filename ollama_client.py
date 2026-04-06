import httpx
import logging
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import OLLAMA_URL, MODEL_NAME, OLLAMA_NUM_CTX, OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)

MODEL_PROFILES = {
    "fast": {
        "models": ["tinyllama", "granite3.1-moe"],
        "description": "Modelo rapido para tarefas simples",
        "supports_tools": False,
        "use_cases": [
            "saudacoes",
            "clima",
            "traducao",
            "notas",
            "lembretes",
            "comandos simples",
        ],
    },
    "smart": {
        "models": ["llama3.2:3b", "qwen2.5:1.5b"],
        "description": "Modelo inteligente para tarefas complexas",
        "supports_tools": True,
        "use_cases": [
            "pesquisa",
            "analise",
            "resumo",
            "geracao de conteudo",
            "programacao",
            "raziocinio",
        ],
    },
}

COMPLEXITY_KEYWORDS = [
    COMPLEXITY_KEYWORDS = [
    "analise",
    "resuma",
    "resumo",
    "explique",
    "compare",
    "porque",
    "como",
    "programacao",
    "codigo",
    "code",
    "debug",
    "pesquise",
    "pesquisa",
    "search",
    "investigue",
    "crie",
    "gere",
    "escreva",
    "liste",
    "detalhe",
    "profundo",
    "complexo",
    "avancado",
]

SIMPLE_KEYWORDS = [
    "ola",
    "oi",
    "hey",
    "bom dia",
    "boa tarde",
    "boa noite",
    "clima",
    "weather",
    "temperatura",
    "traduza",
    "translate",
    "nota",
    "lembrete",
    "hora",
    "data",
    "ajuda",
    "obrigado",
    "valeu",
    "tchau",
]


def analyze_query_complexity(query: str) -> str:
    query_lower = query.lower()

    simple_matches = sum(1 for kw in SIMPLE_KEYWORDS if kw in query_lower)
    complex_matches = sum(1 for kw in COMPLEXITY_KEYWORDS if kw in query_lower)

    word_count = len(query.split())

    has_question = any(
        c in query for c in ["?", "porque", "como", "quando", "onde", "quem"]
    )
    has_code = bool(
        re.search(r"```|def |function |import |class |if |for |while ", query_lower)
    )
    has_urls = bool(re.search(r"https?://|www\.", query_lower))

    complexity_score = (complex_matches * 3) - (simple_matches * 2) + (word_count // 10)
    if has_question:
        complexity_score += 2
    if has_code:
        complexity_score += 3
    if has_urls:
        complexity_score += 1

    if complexity_score <= 0:
        return "fast"
    else:
        return "smart"


def get_model_for_complexity(
    complexity: str,
    current_model: str = MODEL_NAME,
    tools: Optional[List[Dict[str, Any]]] = None,
) -> str:
    if tools:
        # Prefer current model if it supports tools
        for profile in MODEL_PROFILES.values():
            if profile.get("supports_tools") and current_model in profile["models"]:
                return current_model
        # Otherwise use llama3.2:3b as default for tools
        return "llama3.2:3b"

    if complexity == "fast":
        return MODEL_PROFILES["fast"]["models"][0]
    else:
        return current_model


async def call_ollama(
    messages: List[Dict[str, Any]],
    tools: Optional[List[Dict[str, Any]]] = None,
    model: Optional[str] = None,
    smart_routing: bool = True,
) -> Dict[str, Any]:
    if model is None:
        model = MODEL_NAME

    if smart_routing and messages:
        last_user_msg = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break

        if last_user_msg:
            complexity = analyze_query_complexity(last_user_msg)
            routed_model = get_model_for_complexity(complexity, model, tools)
            if routed_model != model:
                logger.info(
                    f"Smart routing: {complexity} -> {routed_model} (original: {model})"
                )
                model = routed_model

    url = f"{OLLAMA_URL}/api/chat"
    payload = {
        "model": model,
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
            logger.info(f"Ollama ({model}) respondeu em {duration:.2f}s")

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


async def switch_model(new_model: str) -> str:
    global MODEL_NAME
    try:
        url = f"{OLLAMA_URL}/api/tags"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                available_models = [m["name"] for m in data.get("models", [])]
                if new_model in available_models:
                    MODEL_NAME = new_model
                    return f"✅ Modelo alterado para: {new_model}"
                else:
                    return f"❌ Modelo '{new_model}' não encontrado. Modelos disponíveis: {', '.join(available_models)}"
            else:
                return f"❌ Erro ao listar modelos: {response.status_code}"
    except Exception as e:
        return f"❌ Erro ao trocar modelo: {str(e)}"


async def list_available_models() -> str:
    try:
        url = f"{OLLAMA_URL}/api/tags"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                if not models:
                    return "Nenhum modelo disponível no Ollama."

                result = "📋 *Modelos Disponíveis:*\n\n"
                for m in models:
                    name = m["name"]
                    size = m.get("size", 0)
                    size_gb = size / (1024**3) if size else 0
                    marker = "⭐" if name == MODEL_NAME else "  "
                    result += f"{marker} `{name}` ({size_gb:.1f} GB)\n"

                result += f"\n🔄 *Modelo atual:* `{MODEL_NAME}`"
                return result
            else:
                return f"❌ Erro ao listar modelos: {response.status_code}"
    except Exception as e:
        return f"❌ Erro ao listar modelos: {str(e)}"
