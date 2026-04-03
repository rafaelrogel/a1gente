from typing import Dict, List, Any, Optional

memory: Dict[str, List[Dict[str, Any]]] = {}


def update_memory(
    channel_id: str,
    role: str,
    content: str,
    tool_calls: Optional[List] = None,
    max_memory: int = 20,
):
    if channel_id not in memory:
        memory[channel_id] = []

    msg = {"role": role, "content": content}
    if tool_calls:
        msg["tool_calls"] = tool_calls

    memory[channel_id].append(msg)

    if len(memory[channel_id]) > max_memory:
        memory[channel_id] = memory[channel_id][-max_memory:]


def get_memory(channel_id: str) -> List[Dict[str, Any]]:
    return memory.get(channel_id, [])


def clear_memory(channel_id: str):
    if channel_id in memory:
        memory[channel_id] = []


def clear_all_memory():
    memory.clear()
