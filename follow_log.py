import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("178.104.56.115", 22, "root", "EspetadaDeGalinha@1", timeout=10)

stdin, stdout, stderr = c.exec_command("journalctl -u a1gente -f -n 5", timeout=10)
print("=== FOLLOWING LOGS ===")
try:
    while True:
        line = stdout.readline()
        if not line:
            break
        safe = "".join(
            x if ord(x) < 128 else "?" for x in line.decode("utf-8", errors="replace")
        )
        print(safe[:120])
except:
    pass

c.close()
