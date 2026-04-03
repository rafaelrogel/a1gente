import pytest
import os
from unittest.mock import patch


@pytest.fixture(autouse=True)
def clean_env():
    env_vars = {
        "SLACK_BOT_TOKEN": "xoxb-test",
        "SLACK_APP_TOKEN": "xapp-test",
        "SLACK_BOT_USER_ID": "U123456",
        "OLLAMA_URL": "http://localhost:11434",
        "MODEL_NAME": "llama3.2:3b",
        "OLLAMA_NUM_CTX": "4096",
        "OLLAMA_TIMEOUT": "600",
        "MAX_MEMORY": "10",
    }
    with patch.dict(os.environ, env_vars, clear=False):
        yield
