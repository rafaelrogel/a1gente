import json
import re
import logging
import os
from typing import List, Dict, Any
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import SCHEDULED_TASKS_FILE

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def load_scheduled_tasks() -> List[Dict[str, Any]]:
    if not SCHEDULED_TASKS_FILE:
        return []
    if isinstance(SCHEDULED_TASKS_FILE, str) and not SCHEDULED_TASKS_FILE:
        return []
    try:
        if isinstance(SCHEDULED_TASKS_FILE, str) and not os.path.exists(
            SCHEDULED_TASKS_FILE
        ):
            return []
    except Exception:
        return []
    try:
        with open(SCHEDULED_TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar tarefas agendadas: {e}")
        return []


def save_scheduled_tasks(tasks: List[Dict[str, Any]]):
    if not SCHEDULED_TASKS_FILE:
        logger.error("SCHEDULED_TASKS_FILE not configured")
        return
    try:
        with open(SCHEDULED_TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erro ao salvar tarefas agendadas: {e}")


def add_task_to_scheduler(task: Dict[str, Any], run_scheduled_task):
    try:
        if "todo dia" in task["recurrence"].lower():
            match = re.search(r"(\d{1,2})[h:](\d{1,2})?", task["recurrence"])
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2)) if match.group(2) else 0
                scheduler.add_job(
                    run_scheduled_task,
                    "cron",
                    hour=hour,
                    minute=minute,
                    args=[task],
                    id=task["id"],
                    replace_existing=True,
                )
                logger.info(
                    f"Tarefa {task['id']} agendada: {hour:02d}:{minute:02d} diariamente."
                )
            else:
                logger.warning(
                    f"Could not parse time from recurrence: {task['recurrence']}"
                )
        else:
            scheduler.add_job(
                run_scheduled_task,
                "interval",
                minutes=60,
                args=[task],
                id=task["id"],
                replace_existing=True,
            )
    except Exception as e:
        logger.error(f"Erro ao adicionar tarefa ao scheduler: {e}")
