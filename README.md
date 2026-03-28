# AI Slack Agent with Ollama

Este projeto implementa um agente inteligente que vive no Slack e utiliza o Ollama como cérebro local. Ele possui ferramentas de pesquisa na web (DuckDuckGo), leitura de sites, geração de blog posts e resumos.

## 🚀 Instalação Rápida (Recomendado para VPS)

Se você estiver em um servidor Ubuntu/Linux, pode usar os scripts automáticos para instalar e configurar tudo como um serviço do sistema:

```bash
# 1. Torne os scripts executáveis
chmod +x install.sh update.sh uninstall.sh

# 2. Rode a instalação
sudo ./install.sh
```

### Comandos úteis:
- **Atualizar o agente**: `./update.sh` (Puxa do Git e reinicia o serviço)
- **Remover tudo**: `sudo ./uninstall.sh`
- **Ver logs**: `journalctl -u a1gente -f`

---

## 🛠️ Instalação Manual

### 1. Requisitos
- Python 3.10+
- Ollama instalado e rodando (`ollama serve`)
- Modelo baixado: `ollama pull llama3.2:3b`

### 2. Configuração do Ambiente
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuração do `.env`
Crie um arquivo `.env` com as seguintes chaves:
```env
SLACK_BOT_TOKEN=xoxb-seu-token-aqui
SLACK_APP_TOKEN=xapp-seu-token-aqui
SLACK_BOT_USER_ID=UXXXXXXXXXX
OLLAMA_URL=http://localhost:11434
MODEL_NAME=llama3.2:3b
```

### 4. Rodar
```bash
python agent.py
```

## 🛠️ Como configurar o Slack

1. Vá para [api.slack.com/apps](https://api.slack.com/apps) e crie um novo App "From scratch".
2. **Socket Mode**: Ative em "Settings > Socket Mode". Gere um App-Level Token com o scope `connections:write`.
3. **OAuth & Permissions**:
   - Vá em "Bot Token Scopes" e adicione:
     - `app_mentions:read`
     - `chat:write`
     - `im:history` e `im:read`
     - `channels:history`
4. **Install App**: Instale para gerar o `SLACK_BOT_TOKEN`.
5. **Event Subscriptions**: Adicione `app_mention` e `message.im`.
