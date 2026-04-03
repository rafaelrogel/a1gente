import pytest
from memory import update_memory, get_memory, clear_memory, clear_all_memory


def test_update_memory():
    clear_all_memory()
    update_memory("channel1", "user", "Hello")
    mem = get_memory("channel1")
    assert len(mem) == 1
    assert mem[0]["role"] == "user"
    assert mem[0]["content"] == "Hello"


def test_memory_limit():
    clear_all_memory()
    for i in range(25):
        update_memory("channel1", "user", f"Message {i}", max_memory=20)
    mem = get_memory("channel1")
    assert len(mem) == 20


def test_multiple_channels():
    clear_all_memory()
    update_memory("channel1", "user", "Hello from channel 1")
    update_memory("channel2", "user", "Hello from channel 2")
    assert len(get_memory("channel1")) == 1
    assert len(get_memory("channel2")) == 1
    assert get_memory("channel1")[0]["content"] == "Hello from channel 1"


def test_clear_memory():
    clear_all_memory()
    update_memory("channel1", "user", "Hello")
    clear_memory("channel1")
    assert get_memory("channel1") == []
