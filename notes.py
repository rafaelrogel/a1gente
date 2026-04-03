import json
import os
import logging
from typing import Optional, Dict, Any
from config import BASE_DIR

logger = logging.getLogger(__name__)

NOTES_FILE = os.path.join(BASE_DIR, "notes.json")


def _load_notes() -> Dict[str, Any]:
    """Load notes from JSON file."""
    if not os.path.exists(NOTES_FILE):
        return {}
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar notas: {e}")
        return {}


def _save_notes(notes: Dict[str, Any]) -> bool:
    """Save notes to JSON file."""
    try:
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(notes, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar notas: {e}")
        return False


async def save_note(key: str, content: str) -> str:
    """
    Save a note with the given key.
    Example: save_note("project-ideas", "Build a bot that...")
    """
    try:
        notes = _load_notes()
        notes[key] = {
            "content": content,
            "updated_at": __import__("datetime").datetime.now().isoformat(),
        }
        if _save_notes(notes):
            return f"Nota salva com sucesso: '{key}'"
        return "ERRO: Falha ao salvar nota"
    except Exception as e:
        logger.error(f"Erro no save_note: {e}")
        return f"ERRO: {str(e)}"


async def get_note(key: str) -> str:
    """
    Retrieve a note by its key.
    Returns the content and timestamp.
    """
    try:
        notes = _load_notes()
        if key in notes:
            note = notes[key]
            return f"Nota: '{key}'\n\n{note['content']}\n\nAtualizado em: {note.get('updated_at', 'desconhecido')}"
        return f"Nota '{key}' não encontrada. Use save_note para criar uma."
    except Exception as e:
        logger.error(f"Erro no get_note: {e}")
        return f"ERRO: {str(e)}"


async def list_notes() -> str:
    """List all note keys."""
    try:
        notes = _load_notes()
        if not notes:
            return "Nenhuma nota salva ainda."
        keys = list(notes.keys())
        return "Notas salvas:\n" + "\n".join(f"- {k}" for k in keys)
    except Exception as e:
        logger.error(f"Erro no list_notes: {e}")
        return f"ERRO: {str(e)}"


async def delete_note(key: str) -> str:
    """Delete a note by its key."""
    try:
        notes = _load_notes()
        if key in notes:
            del notes[key]
            if _save_notes(notes):
                return f"Nota '{key}' deletada com sucesso."
            return "ERRO: Falha ao deletar nota"
        return f"Nota '{key}' não encontrada."
    except Exception as e:
        logger.error(f"Erro no delete_note: {e}")
        return f"ERRO: {str(e)}"
