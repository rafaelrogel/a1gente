import pytest
from memory import update_memory, get_memory, clear_memory, clear_all_memory


@pytest.mark.asyncio
async def test_update_memory():
    clear_all_memory()
    await update_memory("channel1", "user", "Hello")
    mem = get_memory("channel1")
    assert len(mem) == 1
    assert mem[0]["role"] == "user"
    assert mem[0]["content"] == "Hello"


@pytest.mark.asyncio
async def test_memory_limit():
    clear_all_memory()
    for i in range(25):
        await update_memory("channel1", "user", f"Message {i}", max_memory=20)
    mem = get_memory("channel1")
    assert len(mem) == 20


@pytest.mark.asyncio
async def test_memory_limit_preserves_system():
    clear_all_memory()
    await update_memory("channel1", "system", "System prompt", max_memory=20)
    for i in range(25):
        await update_memory("channel1", "user", f"Message {i}", max_memory=20)
    mem = get_memory("channel1")
    assert len(mem) == 20
    assert mem[0]["role"] == "system"
    assert mem[0]["content"] == "System prompt"


@pytest.mark.asyncio
async def test_multiple_channels():
    clear_all_memory()
    await update_memory("channel1", "user", "Hello from channel 1")
    await update_memory("channel2", "user", "Hello from channel 2")
    assert len(get_memory("channel1")) == 1
    assert len(get_memory("channel2")) == 1
    assert get_memory("channel1")[0]["content"] == "Hello from channel 1"


@pytest.mark.asyncio
async def test_clear_memory():
    clear_all_memory()
    await update_memory("channel1", "user", "Hello")
    clear_memory("channel1")
    assert get_memory("channel1") == []


def test_get_memory_returns_list():
    clear_all_memory()
    result = get_memory("nonexistent_channel")
    assert result == []
    assert result is not None
