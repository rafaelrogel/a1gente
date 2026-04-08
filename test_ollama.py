import asyncio
import httpx
import json
import sys

sys.path.insert(0, "/root/a1gente")

from tools import TOOLS


async def test_with_full_tools():
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "llama3.2:3b",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Ative busca automática de vagas"},
        ],
        "tools": TOOLS[:5],
        "stream": False,
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=60.0)
            print(f"Status: {response.status_code}")
            data = response.json()
            if "tool_calls" in data.get("message", {}):
                print(
                    "Tool calls:",
                    json.dumps(data["message"]["tool_calls"], indent=2)[:500],
                )
            else:
                print("Content:", data.get("message", {}).get("content", "")[:200])
        except Exception as e:
            print(f"Error: {e}")


asyncio.run(test_with_full_tools())
