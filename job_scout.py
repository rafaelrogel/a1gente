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
    "Brazilian Portuguese localizer jobs",
    "Translation project manager remote",
    "UX Designer Brazilian Portuguese",
    "Localization specialist Portuguese jobs",
    "Portuguese translator jobs Europe remote",
    "Brazilian Portuguese UX writer jobs",
    "Translation coordinator remote jobs",
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            url TEXT NOT NULL,
            description TEXT,
            score INTEGER DEFAULT 0,
            score_reason TEXT,
            status TEXT DEFAULT 'new',
            applied_at TEXT,
            notes TEXT,
            found_at TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """
    )

    conn.commit()
    conn.close()
    logger.info("Job Scout database initialized")


def generate_job_id(title: str, company: str, url: str) -> str:
    content = f"{title.lower().strip()}-{company.lower().strip()}-{url.lower().strip()}"
    return hashlib.md5(content.encode()).hexdigest()[:12]


def save_job(job: Dict[str, Any]) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        job_id = job.get("job_id")
        cursor.execute("SELECT id FROM jobs WHERE job_id = ?", (job_id,))
        if cursor.fetchone():
            conn.close()
            return False

        now = datetime.now().isoformat()
        cursor.execute(
            """
            INSERT INTO jobs (job_id, title, company, location, url, description, 
                            score, score_reason, status, found_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                job_id,
                job.get("title", ""),
                job.get("company", ""),
                job.get("location", ""),
                job.get("url", ""),
                job.get("description", ""),
                job.get("score", 0),
                job.get("score_reason", ""),
                "new",
                now,
                now,
            ),
        )

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar vaga: {e}")
        return False


def get_jobs(status: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if status:
            cursor.execute(
                "SELECT * FROM jobs WHERE status = ? ORDER BY score DESC, created_at DESC LIMIT ?",
                (status, limit),
            )
        else:
            cursor.execute(
                "SELECT * FROM jobs ORDER BY score DESC, created_at DESC LIMIT ?",
                (limit,),
            )

        jobs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jobs
    except Exception as e:
        logger.error(f"Erro ao buscar vagas: {e}")
        return []


def mark_applied(job_id: str) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        cursor.execute(
            "UPDATE jobs SET status = 'applied', applied_at = ? WHERE job_id = ?",
            (now, job_id),
        )

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erro ao marcar vaga como aplicada: {e}")
        return False


def get_stats() -> Dict[str, Any]:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM jobs")
        total = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as count FROM jobs WHERE status = 'new'")
        new_count = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM jobs WHERE status = 'applied'")
        applied_count = cursor.fetchone()["count"]

        cursor.execute("SELECT AVG(score) as avg_score FROM jobs WHERE score > 0")
        avg_score_row = cursor.fetchone()
        avg_score = (
            round(avg_score_row["avg_score"], 1) if avg_score_row["avg_score"] else 0
        )

        cursor.execute("SELECT MAX(score) as max_score FROM jobs WHERE score > 0")
        max_score_row = cursor.fetchone()
        max_score = max_score_row["max_score"] if max_score_row["max_score"] else 0

        conn.close()
        return {
            "total": total,
            "new": new_count,
            "applied": applied_count,
            "avg_score": avg_score,
            "max_score": max_score,
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatisticas: {e}")
        return {}


def format_job_message(job: Dict[str, Any]) -> str:
    score = job.get("score", 0)
    score_emoji = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"

    msg = f"{score_emoji} *{score}/100* | *#{job.get('job_id')}*\n"
    msg += f"*{job.get('title')}*\n"
    msg += f"🏢 {job.get('company')} | 📍 {job.get('location')}\n"
    msg += f"🔗 {job.get('url')}"

    if job.get("score_reason"):
        msg += f"\n📊 {job.get('score_reason')}"

    if job.get("status") == "applied":
        msg += f"\n✅ *Candidatado em:* {job.get('applied_at', 'N/A')[:10]}"

    return msg


def format_jobs_list(jobs: List[Dict[str, Any]]) -> str:
    if not jobs:
        return "Nenhuma vaga encontrada."

    msg = "🔍 *Vagas Encontradas:*\n\n"
    for job in jobs[:10]:
        score = job.get("score", 0)
        score_emoji = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
        status_emoji = "✅" if job.get("status") == "applied" else "🆕"
        msg += f"{status_emoji} {score_emoji} *{score}* | #{job.get('job_id')} | {job.get('title')[:40]}\n"
        msg += f"  🏢 {job.get('company')} | 📍 {job.get('location')}\n\n"

    return msg


def format_stats_message(stats: Dict[str, Any]) -> str:
    if not stats:
        return "Erro ao obter estatisticas."

    msg = "📊 *Estatisticas de Vagas:*\n\n"
    msg += f"📋 Total de vagas: {stats.get('total', 0)}\n"
    msg += f"🆕 Novas: {stats.get('new', 0)}\n"
    msg += f"✅ Candidatadas: {stats.get('applied', 0)}\n"
    msg += f"📈 Pontuacao media: {stats.get('avg_score', 0)}\n"
    msg += f"🏆 Maior pontuacao: {stats.get('max_score', 0)}"

    return msg


async def search_jobs_and_score() -> List[Dict[str, Any]]:
    """Active job search: uses web search to find jobs, then scores them."""
    from tools import web_search

    all_jobs = []

    for query in SEARCH_QUERIES:
        try:
            search_result = await web_search(query)

            if "ERRO_PESQUISA" in search_result:
                logger.warning(f"Falha na busca: {query}")
                continue

            jobs_from_query = parse_jobs_from_search(search_result, query)
            all_jobs.extend(jobs_from_query)

            await asyncio.sleep(2)

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
