import paramiko
import sys

host = "178.104.56.115"
port = 22
username = "root"
password = "EspetadaDeGalinha@1"

commands = [
    "cd /root/a1gente && git pull origin main",
    "ollama pull tinyllama",
    "ollama pull phi",
    "ollama pull smollm2",
    "ollama pull qwen2.5:1.5b",
    "ollama pull granite3.1-moe",
    "ollama list",
]


def run_command(client, cmd):
    try:
        stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
        output = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        print(f"\n=== {cmd} ===")
        if output.strip():
            print(output.strip()[:2000])
        if err.strip() and "warning" not in err.lower():
            print("ERR:", err.strip()[:500])
    except Exception as e:
        print(f"Error: {e}")


try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port=port, username=username, password=password, timeout=10)

    for cmd in commands:
        run_command(client, cmd)

    client.close()
    print("\n\nModels installed!")
except Exception as e:
    print(f"Connection Error: {e}")
    sys.exit(1)
