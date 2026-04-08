import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("178.104.56.115", 22, "root", "EspetadaDeGalinha@1", timeout=10)
stdin, stdout, stderr = c.exec_command(
    "journalctl -u a1gente -n 80 --no-pager", timeout=15
)
out = stdout.read().decode("utf-8", errors="replace")
lines = out.strip().split("\n")
for l in lines[-40:]:
    safe = "".join(x if ord(x) < 128 else "?" for x in l)
    print(safe[-100:])
c.close()
