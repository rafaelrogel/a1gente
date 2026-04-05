import paramiko

host = "178.104.56.115"
port = 22
username = "root"
password = "EspetadaDeGalinha@1"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

stdin, stdout, stderr = client.exec_command("kill -9 1037926", timeout=10)
print("Killed stuck process")

stdin, stdout, stderr = client.exec_command(
    "ps aux | grep ollama | grep -v grep", timeout=10
)
out = stdout.read().decode("utf-8", errors="replace")
print("Ollama:", out[:300])

client.close()
