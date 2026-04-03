import asyncio
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, ".")


async def test_reddit():
    from reddit_tools import scrape_reddit, search_reddit

    print("=" * 60)
    print("TEST 1: scrape_reddit - Hot posts from r/brasil")
    print("=" * 60)
    result = await scrape_reddit("brasil", sort="hot", limit=5)
    print(result)

    print("\n" + "=" * 60)
    print("TEST 2: scrape_reddit - New posts from r/programming")
    print("=" * 60)
    result = await scrape_reddit("programming", sort="new", limit=5)
    print(result)

    print("\n" + "=" * 60)
    print("TEST 3: search_reddit - Search for 'python programming'")
    print("=" * 60)
    result = await search_reddit("python programming", limit=5)
    print(result)

    print("\n" + "=" * 60)
    print("TEST 4: scrape_reddit - Invalid subreddit")
    print("=" * 60)
    result = await scrape_reddit("thisdoesnotexist12345", sort="hot", limit=3)
    print(result)


asyncio.run(test_reddit())
