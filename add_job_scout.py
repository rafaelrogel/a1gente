import json
import sys

# Read current tasks
try:
    with open("/root/a1gente/scheduled_tasks.json", "r") as f:
        tasks = json.load(f)
except:
    tasks = []

# Add job scout task if not exists
job_scout_task = {
    "id": "auto_job_scout",
    "type": "job_scout",
    "prompt": "Execute a busca automatica de vagas: use a ferramenta search_jobs e poste o resultado no canal C0123456789 se houver novas vagas.",
    "recurrence": "interval_6h",
    "interval_hours": 6,
    "description": "Busca automatica de vagas a cada 6 horas",
    "channel": "C0123456789",
    "created_at": "2026-04-05T20:00:00",
}

# Remove existing job_scout if any
tasks = [t for t in tasks if t.get("id") != "auto_job_scout"]
tasks.append(job_scout_task)

with open("/root/a1gente/scheduled_tasks.json", "w") as f:
    json.dump(tasks, f, indent=2)

print("Done")
