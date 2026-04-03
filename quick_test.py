import paramiko
import sys

host = "178.104.56.115"
port = 22
username = "root"
password = "EspetadaDeGalinha@1"

commands = [
    'time curl -s http://localhost:11434/api/chat -d \'{"model":"tinyllama","messages":[{"role":"user","content":"Hi in 3 words"}],"stream":false}\' | python3 -c "import sys,json; print(json.load(sys.stdin)[\'message\'][\'content\'])"',
    'time curl -s http://localhost:11434/api/chat -d \'{"model":"phi","messages":[{"role":"user","content":"Hi in 3 words"}],"stream":false}\' | python3 -c "import sys,json; print(json.load(sys.stdin)[\'message\'][\'content\'])"',
    'time curl -s http://localhost:11434/api/chat -d \'{"model":"qwen2.5:1.5b","messages":[{"role":"user","content":"Hi in 3 words"}],"stream":false}\' | python3 -c "import sys,json; print(json.load(sys.stdin)[\'message\'][\'content\'])"',
    'time curl -s http://localhost:11434/api/chat -d \'{"model":"llama3.2:3b","messages":[{"role":"user","content":"Hi in 3 words"}],"stream":false}\' | python3 -c "import sys,json; print(json.load(sys.stdin)[\'message"][\'content\'])"',
]


def run_command(client, cmd):
    try:
        stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
        output = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        if output.strip():
            print(output.strip()[:500])
        if err.strip() and "real" not in err.lower():
            print("ERR:", err.strip()[:200])
    except Exception as e:
        print(f"Error: {e}")


try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port=port, username=username, password=password, timeout=10)

    for cmd in commands:
        run_command(client, cmd)
        print()

    client.close()
except Exception as e:
    print(f"Connection Error: {e}")
    sys.exit(1)
