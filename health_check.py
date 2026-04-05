import subprocess
import time
import logging
from datetime import datetime

logging.basicConfig(
    filename="/var/log/agent_health.log",
    level=logging.INFO,
    format="%(asctime)s %(message)s",
)


def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode


def check():
    log = logging.info

    # Check RAM
    out, _ = run("free | grep Mem | awk '{print int($3*100/$2)}'")
    try:
        ram_pct = int(out)
        log(f"RAM: {ram_pct}%")

        if ram_pct > 70:
            log("ALERTA: RAM > 70%")
            run("pkill -f 'ollama runner'")
            run("systemctl restart a1gente")
            log("Agent restarted")
    except:
        pass

    # Check stuck Ollama
    out, _ = run("ps aux | grep 'ollama runner' | grep -v grep | wc -l")
    try:
        count = int(out)
        if count > 1:
            log(f"ALERTA: {count} Ollama runners")
            run("pkill -f 'ollama runner'")
            log("Killed stuck runners")
    except:
        pass

    # Check agent running
    out, _ = run("systemctl is-active a1gente")
    if out != "active":
        log(f"ALERTA: Agent not active: {out}")
        run("systemctl restart a1gente")
        log("Restarted agent")


if __name__ == "__main__":
    check()
