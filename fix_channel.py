import json
import os

tasks_file = "/root/a1gente/scheduled_tasks.json"

with open(tasks_file, "r") as f:
    tasks = json.load(f)

for t in tasks:
    if t.get("id") == "auto_job_scout":
        t["channel"] = "C0ANYSSN4BA"
        t["prompt"] = (
            "Execute a busca automatica de vagas: use a ferramenta search_jobs e poste o resultado no canal C0ANYSSN4BA se houver novas vagas."
        )
        print(f"Updated: {t.get('id')}")

with open(tasks_file, "w") as f:
    json.dump(tasks, f, indent=2)

print("Done!")
