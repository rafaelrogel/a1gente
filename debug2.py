import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("178.104.56.115", 22, "root", "EspetadaDeGalinha@1", timeout=10)

stdin, stdout, stderr = c.exec_command(
    "tail -50 /root/a1gente/nohup.out 2>/dev/null", timeout=10
)
out = stdout.read().decode("utf-8", errors="replace")
print("=== NOHUP OUT ===")
print(out[-1500:] if out else "no file")

c.close()
