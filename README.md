# Nordic-Claw - AI Slack Agent with Ollama

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-orange.svg)

**An intelligent Slack bot powered by local LLMs via Ollama**

[English](#english) | [Português](#português)

</div>

---

## English

### Overview

Nordic-Claw is a Slack bot that uses Ollama (local LLM) as its brain. It features web search, web fetching, blog post generation, weather, translation, notes, and scheduled tasks.

### Features

| Feature | Description |
|---------|-------------|
| **Web Search** | Search the internet using DuckDuckGo |
| **Web Fetching** | Extract clean text from any URL |
| **Blog Posts** | Generate Markdown blog posts |
| **Weather** | Get current weather for any city (OpenWeatherMap) |
| **Translation** | Translate text to 12+ languages (MyMemory API - free) |
| **Notes** | Save, retrieve, list, and delete notes |
| **Direct Messages** | Send DMs to Slack users |
| **Scheduled Tasks** | Schedule recurring tasks (daily, hourly) |

### Prerequisites

- Python 3.10+
- Ollama installed and running (`ollama serve`)
- Model downloaded: `ollama pull llama3.2:3b`

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/rafaelrogel/a1gente.git
cd a1gente

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Configuration

Edit `.env` with your credentials:

```env
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_BOT_USER_ID=UXXXXXXXXXX

# Ollama Configuration
OLLAMA_URL=http://localhost:11434
MODEL_NAME=llama3.2:3b
OLLAMA_NUM_CTX=3072
OLLAMA_TIMEOUT=600.0

# Optional: Weather API (for get_weather tool)
OPENWEATHER_API_KEY=your-api-key

# Memory & Performance
MAX_MEMORY=10
MAX_ITERATIONS=3
```

### Slack App Setup

1. Go to [api.slack.com/apps](https://api.slack.com/apps) and create a new App "From scratch"
2. **Socket Mode**: Enable in "Settings > Socket Mode". Generate an App-Level Token with scope `connections:write`
3. **OAuth & Permissions**:
   - Add Bot Token Scopes:
     - `app_mentions:read`
     - `chat:write`
     - `im:history`, `im:read`
     - `channels:history`
4. **Install App**: Install to workspace to generate `SLACK_BOT_TOKEN`
5. **Event Subscriptions**: Enable `app_mention` and `message.im`

### Running

```bash
# Development
python agent.py

# Production (with systemd)
sudo ./install.sh
```

### Useful Commands

- **Update agent**: `./update.sh` (pulls from Git and restarts)
- **Remove everything**: `sudo ./uninstall.sh`
- **View logs**: `journalctl -u nordicclaw-agent -f`

### Available Tools

| Tool | Description | Example |
|------|-------------|---------|
| `get_weather` | Current weather | `get_weather(city="São Paulo")` |
| `translate_text` | Translation | `translate_text(text="Hello", target_lang="portuguese")` |
| `save_note` | Save a note | `save_note(key="ideas", content="Build a bot...")` |
| `get_note` | Get a note | `get_note(key="ideas")` |
| `list_notes` | List all notes | `list_notes()` |
| `delete_note` | Delete a note | `delete_note(key="ideas")` |
| `send_dm` | Send DM | `send_dm(user_id="U123456", message="Hi!")` |
| `web_search` | Web search | `web_search(query="latest AI news")` |
| `fetch_webpage` | Extract content | `fetch_webpage(url="https://example.com")` |
| `schedule_action` | Schedule task | `schedule_action(prompt="News", recurrence="daily 9h", channel="C123")` |

### Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_memory.py -v
```

---

## Português

### Visão Geral

Nordic-Claw é um bot do Slack que usa Ollama (LLM local) como cérebro. Possui pesquisa web, extração de conteúdo, geração de posts, clima, tradução, notas e tarefas agendadas.

### Funcionalidades

| Funcionalidade | Descrição |
|----------------|------------|
| **Pesquisa Web** | Pesquisa na internet via DuckDuckGo |
| **Extração de Conteúdo** | Extrai texto limpo de qualquer URL |
| **Posts de Blog** | Gera posts em Markdown |
| **Clima** | Clima atual de qualquer cidade (OpenWeatherMap) |
| **Tradução** | Traduz para 12+ idiomas (API MyMemory - gratuito) |
| **Notas** | Salvar, recuperar, listar e deletar notas |
| **Mensagens Diretas** | Enviar DMs para usuários do Slack |
| **Tarefas Agendadas** | Agendar tarefas recorrentes (diárias, horárias) |

### Pré-requisitos

- Python 3.10+
- Ollama instalado e rodando (`ollama serve`)
- Modelo baixado: `ollama pull llama3.2:3b`

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/rafaelrogel/a1gente.git
cd a1gente

# 2. Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure o ambiente
cp .env.example .env
# Edite .env com suas credenciais
```

### Configuração

Edite `.env` com suas credenciais:

```env
# Configuração Slack
SLACK_BOT_TOKEN=xoxb-seu-token-bot
SLACK_APP_TOKEN=xapp-seu-token-app
SLACK_BOT_USER_ID=UXXXXXXXXXX

# Configuração Ollama
OLLAMA_URL=http://localhost:11434
MODEL_NAME=llama3.2:3b
OLLAMA_NUM_CTX=3072
OLLAMA_TIMEOUT=600.0

# Opcional: API de Clima (para ferramenta get_weather)
OPENWEATHER_API_KEY=sua-chave-api

# Memória e Performance
MAX_MEMORY=10
MAX_ITERATIONS=3
```

### Configuração do Slack

1. Vá para [api.slack.com/apps](https://api.slack.com/apps) e crie um novo App "From scratch"
2. **Socket Mode**: Ative em "Settings > Socket Mode". Gere um App-Level Token com scope `connections:write`
3. **OAuth & Permissions**:
   - Adicione Bot Token Scopes:
     - `app_mentions:read`
     - `chat:write`
     - `im:history`, `im:read`
     - `channels:history`
4. **Install App**: Instale no workspace para gerar `SLACK_BOT_TOKEN`
5. **Event Subscriptions**: Ative `app_mention` e `message.im`

### Executando

```bash
# Desenvolvimento
python agent.py

# Produção (com systemd)
sudo ./install.sh
```

### Comandos Úteis

- **Atualizar agente**: `./update.sh` (puxa do Git e reinicia)
- **Remover tudo**: `sudo ./uninstall.sh`
- **Ver logs**: `journalctl -u nordicclaw-agent -f`

### Ferramentas Disponíveis

| Ferramenta | Descrição | Exemplo |
|------------|-----------|---------|
| `get_weather` | Clima atual | `get_weather(city="São Paulo")` |
| `translate_text` | Tradução | `translate_text(text="Hello", target_lang="portuguese")` |
| `save_note` | Salvar nota | `save_note(key="ideias", content="Construir um bot...")` |
| `get_note` | Pegar nota | `get_note(key="ideias")` |
| `list_notes` | Listar notas | `list_notes()` |
| `delete_note` | Deletar nota | `delete_note(key="ideias")` |
| `send_dm` | Enviar DM | `send_dm(user_id="U123456", message="Olá!")` |
| `web_search` | Pesquisa web | `web_search(query="últimas notícias de IA")` |
| `fetch_webpage` | Extrair conteúdo | `fetch_webpage(url="https://exemplo.com")` |
| `schedule_action` | Agendar tarefa | `schedule_action(prompt="Notícias", recurrence="todo dia 9h", channel="C123")` |

### Testes

```bash
# Rodar todos os testes
pytest tests/

# Rodar arquivo de teste específico
pytest tests/test_memory.py -v
```

---

## Project Structure

```
a1gente/
├── agent.py           # Main entry point
├── config.py          # Configuration management
├── memory.py          # Conversation memory
├── ollama_client.py   # Ollama API client
├── scheduler.py       # Task scheduler
├── tools.py           # Tool definitions
├── weather.py         # Weather tool
├── translate.py       # Translation tool
├── notes.py           # Notes storage tool
├── web_utils.py       # Web fetching utilities
├── requirements.txt   # Dependencies
├── .env.example       # Environment template
├── tests/             # Test suite
├── install.sh         # Installation script
├── update.sh          # Update script
└── uninstall.sh       # Uninstallation script
```

## License

MIT License - See LICENSE file for details.
