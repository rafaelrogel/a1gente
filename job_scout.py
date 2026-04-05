import sqlite3
import json
import logging
import asyncio
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import BASE_DIR

logger = logging.getLogger(__name__)

DB_PATH = f"{BASE_DIR}/job_scout.db"

USER_PROFILE = {
    "target_titles": [
        "Brazilian Portuguese Translator",
        "Brazilian Portuguese Localizer",
        "Translation Project Manager",
        "UX Designer",
        "Localization Specialist",
        "Translation Coordinator",
        "Portuguese Linguist",
        "UX Writer",
        "Content Localizer",
    ],
    "locations": ["Brazil", "Europe", "Remote"],
    "keywords": [
        "Brazilian Portuguese",
        "UX",
        "UX Design",
        "Localization",
        "Translation",
    ],
    "priority_companies": [],
    "avoid_companies": [],
}

SEARCH_QUERIES = [
    "Brazilian Portuguese translator remote jobs",
    "Localization specialist Portuguese jobs",
    "UX Designer Brazilian Portuguese",
]


async def search_jobs_and_score() -> List[Dict[str, Any]]:
    """Active job search: uses web search to find jobs, then scores them."""
    from tools import web_search

    all_jobs = []

    for query in SEARCH_QUERIES:
        try:
            search_result = await asyncio.wait_for(web_search(query), timeout=30.0)

            if "ERRO_PESQUISA" in search_result or "NENHUM_RESULTADO" in search_result:
                logger.warning(f"Sem resultados: {query}")
                continue

            jobs_from_query = parse_jobs_from_search(search_result, query)
            all_jobs.extend(jobs_from_query)

            await asyncio.sleep(1)

        except asyncio.TimeoutError:
            logger.warning(f"Timeout na busca: {query}")
            continue
        except Exception as e:
            logger.error(f"Erro na busca '{query}': {e}")

    scored_jobs = []
    for job in all_jobs:
        score = score_job_against_profile(job)
        job["score"] = score["score"]
        job["score_reason"] = score["reason"]
        job["job_id"] = generate_job_id(job["title"], job["company"], job["url"])

        if job["score"] >= 40:
            saved = save_job(job)
            if saved:
                scored_jobs.append(job)
                logger.info(
                    f"Nova vaga encontrada: {job['title']} (score: {job['score']})"
                )

    return scored_jobs


def parse_jobs_from_search(search_result: str, query: str) -> List[Dict[str, Any]]:
    """Parse job listings from web search results."""
    jobs = []

    lines = search_result.split("\n")
    current_job = {}

    for line in lines:
        line = line.strip()
        if not line:
            if current_job.get("title") and current_job.get("url"):
                if not current_job.get("company"):
                    current_job["company"] = "Empresa nao identificada"
                if not current_job.get("location"):
                    current_job["location"] = "Local nao especificado"
                jobs.append(current_job)
                current_job = {}
            continue

        if "http" in line and not current_job.get("url"):
            current_job["url"] = line.split()[-1]
        elif any(
            kw in line.lower()
            for kw in [
                "job",
                "vaga",
                "career",
                "position",
                "engineer",
                "translator",
                "designer",
                "manager",
                "specialist",
            ]
        ):
            if not current_job.get("title"):
                current_job["title"] = line[:150]
            elif not current_job.get("company"):
                current_job["company"] = line[:100]
            elif not current_job.get("location"):
                current_job["location"] = line[:100]

    if current_job.get("title") and current_job.get("url"):
        if not current_job.get("company"):
            current_job["company"] = "Empresa nao identificada"
        if not current_job.get("location"):
            current_job["location"] = "Local nao especificado"
        jobs.append(current_job)

    return jobs


def score_job_against_profile(job: Dict[str, Any]) -> Dict[str, Any]:
    """Score a job against the user profile (0-100)."""
    title = job.get("title", "").lower()
    company = job.get("company", "").lower()
    location = job.get("location", "").lower()
    description = job.get("description", "").lower()
    url = job.get("url", "").lower()

    all_text = f"{title} {company} {location} {description} {url}"
    score = 0
    reasons = []

    for keyword in USER_PROFILE["keywords"]:
        if keyword.lower() in all_text:
            score += 15
            reasons.append(f"Keyword: {keyword}")

    for target_title in USER_PROFILE["target_titles"]:
        if target_title.lower() in all_text:
            score += 25
            reasons.append(f"Title match: {target_title}")
            break

    for loc in USER_PROFILE["locations"]:
        if loc.lower() in all_text:
            score += 10
            reasons.append(f"Location: {loc}")
            break

    if "remote" in all_text:
        score += 10
        reasons.append("Remote opportunity")

    if "brazilian" in all_text or "brazil" in all_text:
        score += 10
        reasons.append("Brazil connection")

    for avoid in USER_PROFILE.get("avoid_companies", []):
        if avoid.lower() in all_text:
            score = 0
            reasons = ["Company in avoid list"]
            break

    score = min(score, 100)

    if not reasons:
        reasons = ["No strong matches found"]

    return {
        "score": score,
        "reason": "; ".join(reasons[:3]),
    }


init_db()
