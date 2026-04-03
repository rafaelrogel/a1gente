import pytest
import os
import tempfile
from unittest.mock import patch


@pytest.fixture(autouse=True)
def clean_notes():
    """Clean notes file before each test."""
    yield
    notes_file = os.path.join(os.path.dirname(__file__), "..", "notes.json")
    if os.path.exists(notes_file):
        os.remove(notes_file)


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    env_vars = {
        "SLACK_BOT_TOKEN": "xoxb-test",
        "SLACK_APP_TOKEN": "xapp-test",
        "SLACK_BOT_USER_ID": "U123456",
        "OLLAMA_URL": "http://localhost:11434",
        "MODEL_NAME": "llama3.2:3b",
        "OLLAMA_NUM_CTX": "4096",
        "OLLAMA_TIMEOUT": "600",
        "MAX_MEMORY": "10",
        "MAX_ITERATIONS": "3",
    }
    with patch.dict(os.environ, env_vars, clear=False):
        yield


def test_language_codes():
    """Test that language codes are properly mapped."""
    from translate import LANGUAGES

    assert LANGUAGES["portuguese"] == "pt"
    assert LANGUAGES["english"] == "en"
    assert LANGUAGES["pt"] == "pt"
    assert LANGUAGES["spanish"] == "es"
    assert LANGUAGES["es"] == "es"
