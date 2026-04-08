import paramiko
import sys

host = "178.104.56.115"
port = 22
username = "root"
password = "EspetadaDeGalinha@1"

commands = [
    "uptime",
    "free -m",
]


def run_command(client, cmd):
    try:
        stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
        output = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        print(f"=== {cmd} ===")
        print(output.strip())
        if err.strip():
            print("ERR:", err.strip())
    except Exception as e:
        print(f"Error: {e}")


try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port=port, username=username, password=password, timeout=10)

    for cmd in commands:
        run_command(client, cmd)

    client.close()
    print("\nDone!")
except Exception as e:
    print(f"Connection Error: {e}")
    sys.exit(1)
