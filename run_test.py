import paramiko
import sys

host = "178.104.56.115"
port = 22
username = "root"
password = "EspetadaDeGalinha@1"

test_code = """
import httpx
import time

models = ["tinyllama", "phi", "qwen2.5:1.5b", "llama3.2:3b", "smollm2", "granite3.1-moe"]
prompt = "Responda em 3 palavras: ola"

for m in models:
    try:
        t0 = time.time()
        r = httpx.post("http://localhost:11434/api/chat", json={"model": m, "messages": [{"role": "user", "content": prompt}], "stream": False}, timeout=60)
        dt = time.time() - t0
        if r.status_code == 200:
            print(f"OK {m}: {dt:.1f}s -> {r.json()[\"message\"][\"content\"][:50]}")
        else:
            print(f"FAIL {m}: {r.status_code}")
    except Exception as e:
        print(f"ERROR {m}: {e}")
"""

commands = [
    f"cat > /tmp/test_models.py << 'EOF'\n{test_code}\nEOF",
    "python3 /tmp/test_models.py",
]


def run_command(client, cmd):
    try:
        stdin, stdout, stderr = client.exec_command(cmd, timeout=180)
        output = stdout.read().decode("utf-8", errors="replace")
        if output.strip():
            print(output.strip())
    except Exception as e:
        print(f"Error: {e}")


try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port=port, username=username, password=password, timeout=10)

    for cmd in commands:
        run_command(client, cmd)

    client.close()
except Exception as e:
    print(f"Connection Error: {e}")
    sys.exit(1)
