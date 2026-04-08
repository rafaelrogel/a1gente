import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("178.104.56.115", 22, "root", "EspetadaDeGalinha@1", timeout=10)

stdin, stdout, stderr = c.exec_command(
    "ps aux | grep -E 'python|ollama' | head -10", timeout=10
)
out = stdout.read().decode("utf-8", errors="replace")
print("=== PROCESSES ===")
for line in out.strip().split("\n"):
    safe = "".join(x if ord(x) < 128 else "?" for x in line)
    print(safe[:120])

stdin, stdout, stderr = c.exec_command("ls -la /root/a1gente/*.db", timeout=10)
out = stdout.read().decode("utf-8", errors="replace")
print("\n=== DB FILES ===")
print(out)

c.close()
