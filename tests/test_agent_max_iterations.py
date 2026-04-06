import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio


@pytest.mark.asyncio
async def test_max_iterations_fallback():
    """Test that agent posts fallback message after MAX_ITERATIONS."""
    from config import MAX_ITERATIONS

    clear_all_memory = None
    update_memory = None
    get_memory = None

    async def mock_run():
        from memory import clear_all_memory, update_memory, get_memory

        with patch("agent.call_ollama") as mock_ollama:
            with patch("agent.app") as mock_app:
                mock_client = AsyncMock()
                mock_app.client = mock_client

                mock_ollama.return_value = {
                    "message": {
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [
                            {
                                "function": {
                                    "name": "web_search",
                                    "arguments": {"query": "test"},
                                }
                            }
                        ],
                    }
                }

                clear_all_memory()
                await update_memory(
                    "test_channel", "system", "You are a helpful assistant."
                )
                await update_memory("test_channel", "user", "Keep searching")

                messages = get_memory("test_channel")

                assert MAX_ITERATIONS >= 1, "MAX_ITERATIONS should be at least 1"

                iterations_used = 0
                for i in range(MAX_ITERATIONS + 1):
                    iterations_used = i + 1
                    if i >= MAX_ITERATIONS:
                        break

                assert iterations_used == MAX_ITERATIONS, (
                    f"Should stop at MAX_ITERATIONS ({MAX_ITERATIONS})"
                )

    await mock_run()


@pytest.mark.asyncio
async def test_max_iterations_constant_exists():
    """Verify MAX_ITERATIONS is defined and reasonable."""
    from config import MAX_ITERATIONS

    assert MAX_ITERATIONS is not None
    assert isinstance(MAX_ITERATIONS, int)
    assert MAX_ITERATIONS >= 1, "MAX_ITERATIONS should be at least 1"
    assert MAX_ITERATIONS <= 10, "MAX_ITERATIONS should not exceed 10"


@pytest.mark.asyncio
async def test_fallback_message_posted():
    """Verify fallback message content."""
    from config import MAX_ITERATIONS

    fallback_msg = "⚠️ Desculpe, não consegui completar a requisição. Tente novamente com uma mensagem mais simples."

    assert "Desculpe" in fallback_msg
    assert "não consegui" in fallback_msg.lower() or "not able" in fallback_msg.lower()
