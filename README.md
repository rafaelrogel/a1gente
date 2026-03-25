# AI Slack Agent with Ollama

Este projeto implementa um agente inteligente que vive no Slack e utiliza o Ollama como cérebro local.

## 🚀 README rápido

### 1. Requisitos
- Python 3.10+
- Ollama instalado e rodando (`ollama serve`)
- Modelo baixado: `ollama pull llama3.2:3b`

### 2. Instalação
```bash
pip install -r requirements.txt
```

### 3. Configuração
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
