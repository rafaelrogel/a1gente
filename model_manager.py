import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

AVAILABLE_MODELS = [
    "llama3.2:3b",
    "tinyllama",
    "qwen2.5:1.5b",
    "granite3.1-moe",
]


def switch_model(model_name: str) -> str:
    """
    Switches the LLM model used by the agent.
    Valid options: llama3.2:3b, tinyllama, phi, smollm2, qwen2.5:1.5b, granite3.1-moe
    """
    global MODEL_NAME
    from config import MODEL_NAME

    normalized = model_name.lower().strip()

    for model in AVAILABLE_MODELS:
        if model.lower() == normalized or model.lower().replace(":", "").replace(
            "-", ""
        ) == normalized.replace(":", "").replace("-", ""):
            from config import MODEL_NAME as current

            if current == model:
                return f"Já estamos usando {model}."

            import config

            config.MODEL_NAME = model

            from memory import clear_all_memory

            clear_all_memory()

            logger.info(f"Model switched to: {model}")
            return f"✅ Modelo trocado para: {model}\n\n⚠️ Contexto limpo."

    return (
        f"Modelo '{model_name}' não disponível. Opções: {', '.join(AVAILABLE_MODELS)}"
    )


def get_current_model() -> str:
    from config import MODEL_NAME

    return MODEL_NAME


def get_available_models() -> list:
    return AVAILABLE_MODELS
