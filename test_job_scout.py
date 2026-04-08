import asyncio
import sys


async def test():
    print("=== TEST 1: search_jobs ===")
    from job_scout import search_jobs_and_score

    try:
        jobs = await search_jobs_and_score()
        print(f"Found {len(jobs)} jobs")
        for j in jobs[:3]:
            title = j.get("title", "?")[:40]
            company = j.get("company", "?")
            score = j.get("score")
            print(f"  - {title} @ {company} ({score}pts)")
    except Exception as e:
        print(f"Error: {e}")

    print("\n=== TEST 2: list_jobs ===")
    from job_scout import get_jobs

    jobs = get_jobs(limit=5)
    print(f"Total saved: {len(jobs)} jobs")
    for j in jobs:
        title = j.get("title", "?")[:30]
        status = j.get("status")
        print(f"  - {title} [{status}]")

    print("\n=== TEST 3: get_stats ===")
    from job_scout import get_stats

    stats = get_stats()
    print(f"Stats: {stats}")

    print("\n=== TEST 4: mark_applied ===")
    if jobs:
        job_id = jobs[0].get("job_id")
        from job_scout import mark_applied

        result = mark_applied(job_id)
        print(f"Marked {job_id}: {result}")

    print("\n=== TEST 5: list_jobs (after apply) ===")
    jobs = get_jobs(status="applied", limit=5)
    print(f"Applied jobs: {len(jobs)}")


if __name__ == "__main__":
    asyncio.run(test())
