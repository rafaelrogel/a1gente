import paramiko
import sys

host = "178.104.56.115"
port = 22
username = "root"
password = "EspetadaDeGalinha@1"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

sftp = client.open_sftp()
sftp.put("health_check.py", "/root/a1gente/health_check.py")
sftp.close()

client.exec_command("chmod +x /root/a1gente/health_check.py", timeout=10)

stdin, stdout, stderr = client.exec_command(
    "crontab -l 2>/dev/null || echo ''", timeout=10
)
current = stdout.read().decode("utf-8", errors="replace").strip()

new_cron = (
    current
    + "\n*/5 * * * * /root/a1gente/venv/bin/python /root/a1gente/health_check.py >> /var/log/agent_health.log 2>&1"
)

stdin, stdout, stderr = client.exec_command(
    f"echo '{new_cron}' | crontab -", timeout=10
)
print("Crontab updated")

client.close()
