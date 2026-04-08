import paramiko

host = "178.104.56.115"
port = 22
username = "root"
password = "EspetadaDeGalinha@1"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

stdin, stdout, stderr = client.exec_command(
    "journalctl -u a1gente -n 60 --no-pager", timeout=15
)
out = stdout.read().decode("utf-8", errors="replace")
lines = out.strip().split("\n")
for line in lines[-50:]:
    safe = "".join(c if ord(c) < 128 else "?" for c in line)
    print(safe)

client.close()
