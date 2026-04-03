import asyncio
import httpx
import time
import sys

MODELS = [
    "llama3.2:3b",
    "tinyllama",
    "phi",
    "smollm2",
    "qwen2.5:1.5b",
    "granite3.1-moe",
]
PROMPTS = [
    ("Portuguese", "Responda em uma frase: qual a capital do Brasil?"),
    ("English", "Answer in one sentence: what is the capital of France?"),
    ("Coding", "Write a simple Python function to check if a number is prime."),
    ("News", "Liste 3 notícias recentes sobre IA (responda apenas com os títulos)."),
]


async def test_model(model: str, prompt: str) -> tuple:
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"num_ctx": 512},
    }

    start = time.time()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=120.0)
            duration = time.time() - start

            if response.status_code == 200:
                result = response.json()
                content = result.get("message", {}).get("content", "")[:200]
                return (True, duration, content)
            else:
                return (False, duration, f"Error: {response.status_code}")
    except Exception as e:
        return (False, time.time() - start, str(e)[:100])


async def run_tests():
    print("=" * 80)
    print("MODEL COMPARISON TEST")
    print("=" * 80)

    results = {}

    for model in MODELS:
        print(f"\n🔄 Testing: {model}")
        model_results = []

        for task_name, prompt in PROMPTS:
            success, duration, content = await test_model(model, prompt)
            status = "✅" if success else "❌"
            print(f"  {status} {task_name}: {duration:.1f}s")
            if success:
                print(f"     → {content[:100]}...")
            else:
                print(f"     → {content}")
            model_results.append((task_name, success, duration))

        results[model] = model_results

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print(
        f"\n{'Model':<20} {'Size':<10} {'Portuguese':<12} {'English':<12} {'Coding':<12} {'News':<12} {'Avg Time':<10}"
    )
    print("-" * 80)

    sizes = {
        "llama3.2:3b": "2.0 GB",
        "tinyllama": "637 MB",
        "phi": "1.6 GB",
        "smollm2": "1.8 GB",
        "qwen2.5:1.5b": "986 MB",
        "granite3.1-moe": "2.0 GB",
    }

    for model in MODELS:
        r = results[model]
        times = [dur for _, success, dur in r if success]
        avg = sum(times) / len(times) if times else 999
        pt = "✓" if r[0][1] else "✗"
        en = "✓" if r[1][1] else "✗"
        code = "✓" if r[2][1] else "✗"
        news = "✓" if r[3][1] else "✗"
        print(
            f"{model:<20} {sizes.get(model, '?'):<10} {pt:<12} {en:<12} {code:<12} {news:<12} {avg:<10.1f}s"
        )


asyncio.run(run_tests())
