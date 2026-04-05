import json
import re
import logging
import os
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import SCHEDULED_TASKS_FILE

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

REPORT_CONFIGS = {
    "daily_briefing": {
        "name": "Daily Briefing",
        "description": "Relatorio diario com clima, noticias e atividades",
        "default_time": "09:00",
        "prompt_template": "Gerar um relatorio diario (Daily Briefing) com:\n1. Resumo do clima atual\n2. Principais noticias do dia\n3. Atividade recente do GitHub\n4. Posts populares do Reddit\n5. Resumo conciso em portugues",
    },
    "morning_news": {
        "name": "Morning News",
        "description": "Noticias da manha resumidas",
        "default_time": "08:00",
        "prompt_template": "Buscar e resumir as principais noticias da manha em portugues. Incluir: tecnologia, negocios e ciencia.",
    },
    "evening_summary": {
        "name": "Evening Summary",
        "description": "Resumo do dia ao entardecer",
        "default_time": "18:00",
        "prompt_template": "Gerar um resumo do dia em portugues. Incluir: eventos importantes, tendencias e destaques.",
    },
    "weekly_report": {
        "name": "Weekly Report",
        "description": "Relatorio semanal completo",
        "default_time": "17:00",
        "prompt_template": "Gerar um relatorio semanal completo em portugues. Incluir: resumo da semana, tendencias, eventos importantes e previsao para a proxima semana.",
    },
}

JOB_SCOUT_TASK = {
    "id": "auto_job_scout",
    "type": "job_scout",
    "prompt": "Execute a busca automatica de vagas: use a ferramenta search_jobs e poste o resultado no canal #A1brella se houver novas vagas.",
    "recurrence": "interval_6h",
    "description": "Busca automatica de vagas a cada 6 horas",
}


def get_available_reports() -> List[Dict[str, str]]:
    return [
        {
            "id": report_id,
            "name": config["name"],
            "description": config["description"],
            "default_time": config["default_time"],
        }
        for report_id, config in REPORT_CONFIGS.items()
    ]


def get_report_prompt(report_type: str) -> Optional[str]:
    if report_type in REPORT_CONFIGS:
        return REPORT_CONFIGS[report_type]["prompt_template"]
    return None


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
        elif "interval" in task.get("recurrence", "").lower():
            interval_match = re.search(r"interval_(\d+)h", task["recurrence"])
            if interval_match:
                hours = int(interval_match.group(1))
                scheduler.add_job(
                    run_scheduled_task,
                    "interval",
                    hours=hours,
                    args=[task],
                    id=task["id"],
                    replace_existing=True,
                )
                logger.info(f"Tarefa {task['id']} agendada: a cada {hours} horas.")
            else:
                scheduler.add_job(
                    run_scheduled_task,
                    "interval",
                    minutes=60,
                    args=[task],
                    id=task["id"],
                    replace_existing=True,
                )
                logger.info(f"Tarefa {task['id']} agendada: a cada 60 minutos.")
    except Exception as e:
        logger.error(f"Erro ao adicionar tarefa ao scheduler: {e}")


def add_report_to_scheduler(
    report_type: str,
    channel: str,
    time_str: Optional[str] = None,
    run_scheduled_task=None,
):
    try:
        if report_type not in REPORT_CONFIGS:
            logger.error(f"Tipo de relatorio desconhecido: {report_type}")
            return None

        config = REPORT_CONFIGS[report_type]
        if time_str is None:
            time_str = config["default_time"]

        match = re.search(r"(\d{1,2})[h:](\d{1,2})?", time_str)
        if not match:
            logger.error(f"Formato de tempo invalido: {time_str}")
            return None

        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0

        task = {
            "id": f"report_{report_type}_{int(datetime.now().timestamp())}",
            "prompt": config["prompt_template"],
            "recurrence": f"todo dia as {hour:02d}:{minute:02d}",
            "channel": channel,
            "type": "report",
            "report_type": report_type,
            "created_at": datetime.now().isoformat(),
        }

        if run_scheduled_task:
            scheduler.add_job(
                run_scheduled_task,
                "cron",
                hour=hour,
                minute=minute,
                args=[task],
                id=task["id"],
                replace_existing=True,
            )

        tasks = load_scheduled_tasks()
        tasks.append(task)
        save_scheduled_tasks(tasks)

        logger.info(
            f"Relatorio {report_type} agendado: {hour:02d}:{minute:02d} no canal {channel}"
        )
        return task

    except Exception as e:
        logger.error(f"Erro ao agendar relatorio: {e}")
        return None


def remove_report_from_scheduler(task_id: str) -> bool:
    try:
        scheduler.remove_job(task_id)

        tasks = load_scheduled_tasks()
        tasks = [t for t in tasks if t.get("id") != task_id]
        save_scheduled_tasks(tasks)

        logger.info(f"Relatorio {task_id} removido do scheduler")
        return True
    except Exception as e:
        logger.error(f"Erro ao remover relatorio do scheduler: {e}")
        return False


def list_active_reports() -> List[Dict[str, Any]]:
    try:
        tasks = load_scheduled_tasks()
        reports = [t for t in tasks if t.get("type") == "report"]
        return reports
    except Exception as e:
        logger.error(f"Erro ao listar relatorios ativos: {e}")
        return []


def add_job_scout_task(run_scheduled_task, interval_hours: int = 6):
    try:
        task = JOB_SCOUT_TASK.copy()
        task["recurrence"] = f"interval_{interval_hours}h"
        task["interval_hours"] = interval_hours

        scheduler.add_job(
            run_scheduled_task,
            "interval",
            hours=interval_hours,
            args=[task],
            id=task["id"],
            replace_existing=True,
        )

        tasks = load_scheduled_tasks()
        existing = [t for t in tasks if t.get("id") != task["id"]]
        existing.append(task)
        save_scheduled_tasks(existing)

        logger.info(f"Job Scout agendado a cada {interval_hours} horas")
        return task
    except Exception as e:
        logger.error(f"Erro ao agendar job scout: {e}")
        return None


def remove_job_scout_task() -> bool:
    try:
        scheduler.remove_job("auto_job_scout")

        tasks = load_scheduled_tasks()
        tasks = [t for t in tasks if t.get("id") != "auto_job_scout"]
        save_scheduled_tasks(tasks)

        logger.info("Job Scout removido do scheduler")
        return True
    except Exception as e:
        logger.error(f"Erro ao remover job scout: {e}")
        return False


def is_job_scout_active() -> bool:
    try:
        tasks = load_scheduled_tasks()
        return any(t.get("id") == "auto_job_scout" for t in tasks)
    except Exception:
        return False
