import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("178.104.56.115", 22, "root", "EspetadaDeGalinha@1", timeout=10)

stdin, stdout, stderr = c.exec_command(
    "cat /root/a1gente/.env | grep SLACK_", timeout=10
)
out = stdout.read().decode("utf-8", errors="replace")
print("Slack config:")
print(out[:400])

c.close()
