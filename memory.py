from typing import Dict, List, Any, Optional
import asyncio

memory: Dict[str, List[Dict[str, Any]]] = {}
channel_locks: Dict[str, asyncio.Lock] = {}


def get_channel_lock(channel_id: str) -> asyncio.Lock:
    if channel_id not in channel_locks:
        channel_locks[channel_id] = asyncio.Lock()
    return channel_locks[channel_id]


async def update_memory(
    channel_id: str,
    role: str,
    content: str,
    tool_calls: Optional[List] = None,
    max_memory: int = 20,
):
    async with get_channel_lock(channel_id):
        if channel_id not in memory:
            memory[channel_id] = []

        msg = {"role": role, "content": content}
        if tool_calls:
            msg["tool_calls"] = tool_calls

        memory[channel_id].append(msg)

        if len(memory[channel_id]) > max_memory:
            if memory[channel_id] and memory[channel_id][0].get("role") == "system":
                system_msg = memory[channel_id][0]
                remaining = memory[channel_id][1:]
                remaining = remaining[-(max_memory - 1) :]
                memory[channel_id] = [system_msg] + remaining
            else:
                memory[channel_id] = memory[channel_id][-max_memory:]


def get_memory(channel_id: str) -> List[Dict[str, Any]]:
    return memory.get(channel_id, []) or []


def clear_memory(channel_id: str):
    if channel_id in memory:
        memory[channel_id] = []


def clear_all_memory():
    memory.clear()
    channel_locks.clear()
