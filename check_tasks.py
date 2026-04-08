import paramiko
import json

host = "178.104.56.115"
port = 22
username = "root"
password = "EspetadaDeGalinha@1"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

stdin, stdout, stderr = client.exec_command(
    "cat /root/a1gente/scheduled_tasks.json", timeout=10
)
out = stdout.read().decode("utf-8", errors="replace")
tasks = json.loads(out)

print("=== Job Scout Task ===")
for t in tasks:
    if "job_scout" in t.get("id", ""):
        print(json.dumps(t, indent=2))

print("\n=== All tasks ===")
for t in tasks:
    print(f"{t.get('id')}: {t.get('channel')}")

client.close()
