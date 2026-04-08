import paramiko

host = "178.104.56.115"
port = 22
username = "root"
password = "EspetadaDeGalinha@1"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

stdin, stdout, stderr = client.exec_command(
    "journalctl -u a1gente -p err -n 20 --no-pager", timeout=15
)
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
print("ERRORS:")
print(out[:3000] if out else "No errors")
if err:
    print("STDERR:", err[:500])

client.close()
