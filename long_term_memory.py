import sqlite3
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from config import BASE_DIR

logger = logging.getLogger(__name__)

DB_PATH = f"{BASE_DIR}/long_term_memory.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT PRIMARY KEY,
            preferences TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS important_facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fact TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'general',
            source TEXT DEFAULT 'user',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversation_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT NOT NULL,
            summary TEXT NOT NULL,
            date TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            tags TEXT DEFAULT '[]',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """
    )

    conn.commit()
    conn.close()
    logger.info("Long-term memory database initialized")


def store_user_preference(user_id: str, key: str, value: Any) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT preferences FROM user_preferences WHERE user_id = ?", (user_id,)
        )
        row = cursor.fetchone()

        if row:
            preferences = json.loads(row["preferences"])
        else:
            preferences = {}

        preferences[key] = value

        cursor.execute(
            """
            INSERT OR REPLACE INTO user_preferences (user_id, preferences, updated_at)
            VALUES (?, ?, ?)
        """,
            (user_id, json.dumps(preferences), datetime.now().isoformat()),
        )

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erro ao armazenar preferencia do usuario: {e}")
        return False


def get_user_preference(user_id: str, key: str, default: Any = None) -> Any:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT preferences FROM user_preferences WHERE user_id = ?", (user_id,)
        )
        row = cursor.fetchone()

        if row:
            preferences = json.loads(row["preferences"])
            conn.close()
            return preferences.get(key, default)

        conn.close()
        return default
    except Exception as e:
        logger.error(f"Erro ao obter preferencia do usuario: {e}")
        return default


def get_all_user_preferences(user_id: str) -> Dict[str, Any]:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT preferences FROM user_preferences WHERE user_id = ?", (user_id,)
        )
        row = cursor.fetchone()

        if row:
            preferences = json.loads(row["preferences"])
            conn.close()
            return preferences

        conn.close()
        return {}
    except Exception as e:
        logger.error(f"Erro ao obter todas as preferencias do usuario: {e}")
        return {}


def store_important_fact(
    fact: str, category: str = "general", source: str = "user"
) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        cursor.execute(
            """
            INSERT INTO important_facts (fact, category, source, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """,
            (fact, category, source, now, now),
        )

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erro ao armazenar fato importante: {e}")
        return False


def get_important_facts(
    category: Optional[str] = None, limit: int = 10
) -> List[Dict[str, Any]]:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if category:
            cursor.execute(
                "SELECT * FROM important_facts WHERE category = ? ORDER BY created_at DESC LIMIT ?",
                (category, limit),
            )
        else:
            cursor.execute(
                "SELECT * FROM important_facts ORDER BY created_at DESC LIMIT ?",
                (limit,),
            )

        facts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return facts
    except Exception as e:
        logger.error(f"Erro ao obter fatos importantes: {e}")
        return []


def search_important_facts(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM important_facts 
            WHERE fact LIKE ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """,
            (f"%{query}%", limit),
        )

        facts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return facts
    except Exception as e:
        logger.error(f"Erro ao buscar fatos importantes: {e}")
        return []


def delete_important_fact(fact_id: int) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM important_facts WHERE id = ?", (fact_id,))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erro ao deletar fato importante: {e}")
        return False


def store_conversation_summary(
    channel_id: str, summary: str, date: Optional[str] = None
) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        now = datetime.now().isoformat()
        cursor.execute(
            """
            INSERT INTO conversation_summaries (channel_id, summary, date, created_at)
            VALUES (?, ?, ?, ?)
        """,
            (channel_id, summary, date, now),
        )

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erro ao armazenar resumo da conversa: {e}")
        return False


def get_conversation_summaries(channel_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM conversation_summaries 
            WHERE channel_id = ? 
            ORDER BY date DESC 
            LIMIT ?
        """,
            (channel_id, limit),
        )

        summaries = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return summaries
    except Exception as e:
        logger.error(f"Erro ao obter resumos da conversa: {e}")
        return []


def store_user_note(
    user_id: str, title: str, content: str, tags: Optional[List[str]] = None
) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        tags_json = json.dumps(tags or [])

        cursor.execute(
            """
            INSERT INTO user_notes (user_id, title, content, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (user_id, title, content, tags_json, now, now),
        )

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erro ao armazenar nota do usuario: {e}")
        return False


def get_user_notes(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM user_notes 
            WHERE user_id = ? 
            ORDER BY updated_at DESC 
            LIMIT ?
        """,
            (user_id, limit),
        )

        notes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return notes
    except Exception as e:
        logger.error(f"Erro ao obter notas do usuario: {e}")
        return []


def search_user_notes(user_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM user_notes 
            WHERE user_id = ? AND (title LIKE ? OR content LIKE ?)
            ORDER BY updated_at DESC 
            LIMIT ?
        """,
            (user_id, f"%{query}%", f"%{query}%", limit),
        )

        notes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return notes
    except Exception as e:
        logger.error(f"Erro ao buscar notas do usuario: {e}")
        return []


def delete_user_note(user_id: str, note_id: int) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM user_notes WHERE id = ? AND user_id = ?", (note_id, user_id)
        )

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erro ao deletar nota do usuario: {e}")
        return False


def get_memory_context_for_user(user_id: str) -> str:
    context_parts = []

    preferences = get_all_user_preferences(user_id)
    if preferences:
        context_parts.append(
            f"Preferencias do usuario: {json.dumps(preferences, ensure_ascii=False)}"
        )

    recent_facts = get_important_facts(limit=5)
    if recent_facts:
        facts_text = "\n".join(
            [f"- {f['fact']} (categoria: {f['category']})" for f in recent_facts]
        )
        context_parts.append(f"Fatos importantes recentes:\n{facts_text}")

    if context_parts:
        return "\n\n".join(context_parts)

    return ""


init_db()
