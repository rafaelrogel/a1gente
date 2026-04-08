import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
SLACK_BOT_USER_ID = os.environ.get("SLACK_BOT_USER_ID")
OLLAMA_URL = (
    os.environ.get("OLLAMA_URL")
    or os.environ.get("OLLAMA_BASE_URL")
    or "http://localhost:11434"
)

MODEL_NAME = {
    "value": os.environ.get("MODEL_NAME") or os.environ.get("MODEL") or "llama3.2:3b"
}

try:
    OLLAMA_NUM_CTX = int(os.environ.get("OLLAMA_NUM_CTX") or "4096")
except ValueError:
    logger.warning("⚠️ OLLAMA_NUM_CTX inválido, usando valor padrão: 4096")
    OLLAMA_NUM_CTX = 4096

try:
    OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT") or "120")
except ValueError:
    logger.warning("⚠️ OLLAMA_TIMEOUT inválido, usando valor padrão: 120")
    OLLAMA_TIMEOUT = 120

try:
    MAX_MEMORY = int(os.environ.get("MAX_MEMORY") or "10")
except ValueError:
    logger.warning("⚠️ MAX_MEMORY inválido, usando valor padrão: 10")
    MAX_MEMORY = 10

try:
    MAX_ITERATIONS = int(os.environ.get("MAX_ITERATIONS") or "3")
except ValueError:
    logger.warning("⚠️ MAX_ITERATIONS inválido, usando valor padrão: 3")
    MAX_ITERATIONS = 3

OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
GIPHY_API_KEY = os.environ.get("GIPHY_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

SMART_ROUTING_ENABLED = (
    os.environ.get("SMART_ROUTING_ENABLED", "true").lower() == "true"
)
FAST_MODEL = os.environ.get("FAST_MODEL") or "tinyllama"
A1MBRA_CHANNEL = os.environ.get("A1MBRA_CHANNEL") or "C0123456789"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEDULED_TASKS_FILE = os.environ.get("SCHEDULED_TASKS_FILE") or os.path.join(
    BASE_DIR, "scheduled_tasks.json"
)


def validate_config():
    missing = []
    if not SLACK_BOT_TOKEN:
        missing.append("SLACK_BOT_TOKEN")
    if not SLACK_APP_TOKEN:
        missing.append("SLACK_APP_TOKEN")
    if not SLACK_BOT_USER_ID:
        missing.append("SLACK_BOT_USER_ID")
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}"
        )


def log_config_warnings():
    if not SLACK_BOT_TOKEN:
        logger.warning(
            "⚠️ Config: SLACK_BOT_TOKEN não está definido. Bot não poderá conectar ao Slack."
        )
    if not SLACK_APP_TOKEN:
        logger.warning(
            "⚠️ Config: SLACK_APP_TOKEN não está definido. Bot não poderá conectar ao Slack."
        )
    if not OLLAMA_URL or OLLAMA_URL == "http://localhost:11434":
        logger.warning(
            "⚠️ Config: OLLAMA_URL não está definido. Usando valor padrão: http://localhost:11434"
        )
    if not MODEL_NAME["value"]:
        logger.warning(
            "⚠️ Config: MODEL_NAME não está definido. Usando valor padrão: llama3.2:3b"
        )
    if not OPENWEATHER_API_KEY:
        logger.warning(
            "⚠️ Config: OPENWEATHER_API_KEY não está definido. Comandos de clima podem falhar."
        )
    if not GIPHY_API_KEY:
        logger.warning(
            "⚠️ Config: GIPHY_API_KEY não está definido. Busca de GIFs pode falhar."
        )
    if not GITHUB_TOKEN:
        logger.warning(
            "⚠️ Config: GITHUB_TOKEN não está definido. Atividade do GitHub pode falhar."
        )


log_config_warnings()
