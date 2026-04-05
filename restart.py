import paramiko

host = "178.104.56.115"
port = 22
username = "root"
password = "EspetadaDeGalinha@1"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

stdin, stdout, stderr = client.exec_command("pkill -f ollama runner", timeout=10)
print("Killed stuck ollama runners")

stdin, stdout, stderr = client.exec_command("systemctl restart a1gente", timeout=10)
print("Agent restarted")

client.close()
