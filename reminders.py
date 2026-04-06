import json
import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import BASE_DIR

logger = logging.getLogger(__name__)

REMINDERS_FILE = os.path.join(BASE_DIR, "reminders.json")

_scheduler = AsyncIOScheduler()


def _load_reminders() -> Dict[str, Any]:
    if not os.path.exists(REMINDERS_FILE):
        return {}
    try:
        with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar lembretes: {e}")
        return {}


def _save_reminders(reminders: Dict[str, Any]) -> bool:
    try:
        with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(reminders, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar lembretes: {e}")
        return False


def _run_reminder(reminder_id: str, user_id: str, text: str, channel_id: str, app):
    asyncio.create_task(_send_reminder(reminder_id, user_id, text, channel_id, app))


async def _send_reminder(
    reminder_id: str, user_id: str, text: str, channel_id: str, app
):
    try:
        message = f"🔔 *Lembrete:* {text}"

        try:
            result = await app.client.conversations_open(users=user_id)
            dm_channel = result["channel"]["id"]
            await app.client.chat_postMessage(channel=dm_channel, text=message)
        except Exception as slack_error:
            logger.error(
                f"Erro ao enviar lembrete via Slack para {user_id}: {slack_error}"
            )
            if channel_id:
                try:
                    await app.client.chat_postMessage(
                        channel=channel_id,
                        text=f"⚠️ Não foi possível enviar DM. Lembrete: {text}",
                    )
                except Exception as fallback_error:
                    logger.error(
                        f"Erro ao enviar fallback para canal {channel_id}: {fallback_error}"
                    )
            return

        reminders = _load_reminders()
        if reminder_id in reminders:
            del reminders[reminder_id]
            _save_reminders(reminders)
    except Exception as e:
        logger.error(f"Erro inesperado ao processar lembrete {reminder_id}: {e}")


async def set_reminder(
    text: str, minutes: int, user_id: str, channel_id: str = None
) -> str:
    """
    Define um lembrete que enviará uma mensagem via DM após o tempo especificado.

    Args:
        text: Texto do lembrete
        minutes: Minutos até o lembrete ser acionado
        user_id: ID do usuário Slack para enviar o DM
        channel_id: Canal opcional para resposta (vai para DM se não especificado)
    """
    try:
        if not isinstance(minutes, (int, float)):
            return "❌ Erro: minutos deve ser um número."

        minutes = int(minutes)

        if minutes < 1:
            return "❌ Erro: o lembrete deve ser definido para pelo menos 1 minuto."

        if minutes > 10080:
            return "❌ Erro: o lembrete não pode ser definido para mais de 7 dias (10080 minutos)."

        reminder_id = f"reminder_{datetime.now().timestamp()}"
        run_time = datetime.now() + timedelta(minutes=minutes)

        reminders = _load_reminders()
        reminders[reminder_id] = {
            "text": text,
            "user_id": user_id,
            "channel_id": channel_id,
            "minutes": minutes,
            "created_at": datetime.now().isoformat(),
        }
        _save_reminders(reminders)

        from agent import app

        job = _scheduler.add_job(
            _run_reminder,
            "date",
            run_date=run_time,
            args=[reminder_id, user_id, text, channel_id, app],
            id=reminder_id,
        )

        if not _scheduler.running:
            _scheduler.start()

        return f"✅ Lembrete definido! Vou te avisar em {minutes} minuto(s)."
    except Exception as e:
        logger.error(f"Erro ao definir lembrete: {e}")
        return f"❌ Erro ao definir lembrete: {str(e)}"


def get_pending_reminders() -> list:
    """Retorna lista de lembretes pendentes."""
    reminders = _load_reminders()
    return [
        {
            "id": k,
            "text": v["text"],
            "minutes": v["minutes"],
            "created": v["created_at"],
        }
        for k, v in reminders.items()
    ]


def init_scheduler():
    """Inicializa o scheduler de lembretes."""
    if not _scheduler.running:
        _scheduler.start()
