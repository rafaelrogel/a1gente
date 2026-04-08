import asyncio
import sys

sys.path.insert(0, "/root/a1gente")


async def test():
    from ollama_client import list_available_models

    result = await list_available_models()
    print(result)


asyncio.run(test())
