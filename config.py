import os
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
SLACK_BOT_USER_ID = os.environ.get("SLACK_BOT_USER_ID")
OLLAMA_URL = (
    os.environ.get("OLLAMA_URL")
    or os.environ.get("OLLAMA_BASE_URL")
    or "http://localhost:11434"
)
MODEL_NAME = os.environ.get("MODEL_NAME") or os.environ.get("MODEL") or "llama3.2:3b"
OLLAMA_NUM_CTX = int(os.environ.get("OLLAMA_NUM_CTX") or 3072)
OLLAMA_TIMEOUT = float(os.environ.get("OLLAMA_TIMEOUT") or 600.0)
MAX_MEMORY = int(os.environ.get("MAX_MEMORY") or 10)
MAX_ITERATIONS = int(os.environ.get("MAX_ITERATIONS") or 3)

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
