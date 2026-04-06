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

Nordic-Claw is a Slack bot that uses Ollama (local LLM) as its brain. It features web search, web fetching, blog post generation, weather, translation, notes, scheduled tasks, job hunting, image generation, Python execution, system administration, and long-term memory.

### Features

| Feature | Description |
|---------|-------------|
| **Web Search** | Search the internet using DuckDuckGo with rate limit handling |
| **Web Fetching** | Extract clean text from any URL |
| **Blog Posts** | Generate Markdown blog posts |
| **Weather** | Get current weather for any city (OpenWeatherMap) |
| **Translation** | Translate text to 12+ languages (MyMemory API - free) |
| **Notes** | Save, retrieve, list, and delete notes |
| **Direct Messages** | Send DMs to Slack users |
| **Reminders** | One-time reminders sent via DM |
| **GIFs** | Search and share GIFs via Giphy |
| **GitHub** | View repository activity (PRs, issues) |
| **Reddit** | Browse subreddits or search Reddit |
| **Scheduled Tasks** | Schedule recurring tasks (daily, hourly, interval) |
| **Job Scout** | Automatic job hunting with scoring and persistence |
| **Image Generation** | Generate images from text prompts (Pollinations.ai) |
| **Python Execution** | Execute safe Python code on the VPS |
| **System Admin** | Run safe system commands for diagnostics |
| **Long-term Memory** | Store and recall user preferences and facts |
| **Model Switching** | Switch between LLM models dynamically |
| **Smart Routing** | Automatically route simple queries to fast models |

### Prerequisites

- Python 3.10+
- Ollama installed and running (`ollama serve`)
- Model downloaded: `ollama pull llama3.2:3b`

### ⚠️ Security Warning

**NEVER commit the `.env` file to GitHub!**

Your `.env` file contains sensitive credentials:
- `SLACK_BOT_TOKEN`
- `SLACK_APP_TOKEN`
- `OPENWEATHER_API_KEY`
- `GIPHY_API_KEY`
- `GITHUB_TOKEN`

This repository uses `.gitignore` to exclude `.env`, but always verify before pushing:
```bash
# Check if .env is in git status - it should NOT be!
git status
# If .env appears, run: git restore .env
```

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
OLLAMA_NUM_CTX=4096
OLLAMA_TIMEOUT=120

# Optional APIs
OPENWEATHER_API_KEY=your-api-key
GIPHY_API_KEY=your-giphy-key
GITHUB_TOKEN=your-github-token

# Memory & Performance
MAX_MEMORY=10
MAX_ITERATIONS=3

# Smart Routing
SMART_ROUTING_ENABLED=true
FAST_MODEL=tinyllama

# Job Scout (optional custom queries)
JOB_SCOUT_QUERIES=Product Designer remote|UX Designer Brazil|Localization Portuguese
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
| `web_search` | Search the web | `web_search(query="latest AI news")` |
| `fetch_webpage` | Extract content from URL | `fetch_webpage(url="https://example.com")` |
| `get_weather` | Current weather | `get_weather(city="São Paulo", units="celsius")` |
| `translate_text` | Translation | `translate_text(text="Hello", target_lang="portuguese")` |
| `save_note` | Save a note | `save_note(key="ideas", content="Build a bot...")` |
| `get_note` | Get a note | `get_note(key="ideas")` |
| `list_notes` | List all notes | `list_notes()` |
| `delete_note` | Delete a note | `delete_note(key="ideas")` |
| `send_dm` | Send DM | `send_dm(user_id="U123456", message="Hi!")` |
| `set_reminder` | One-time reminder | `set_reminder(text="Meeting", minutes=30, user_id="U123")` |
| `search_gif` | Search GIFs | `search_gif(query="happy", limit=5)` |
| `get_github_activity` | GitHub repo activity | `get_github_activity(repo="owner/repo", days=7)` |
| `scrape_reddit` | Subreddit posts | `scrape_reddit(subreddit="brasil", sort="hot", limit=10)` |
| `search_reddit` | Search Reddit | `search_reddit(query="python tips", limit=10)` |
| `schedule_action` | Schedule task | `schedule_action(prompt="News", recurrence="todo dia às 9h", channel="C123")` |
| `search_jobs` | Hunt for jobs | `search_jobs()` |
| `list_jobs` | List saved jobs | `list_jobs(status="new", limit=10)` |
| `mark_job_applied` | Mark job as applied | `mark_job_applied(job_id="abc123")` |
| `get_job_stats` | Job statistics | `get_job_stats()` |
| `generate_image` | Generate image | `generate_image(prompt="a cat on a beach", width=512, height=512)` |
| `execute_python_code` | Run Python | `execute_python_code(code="print(2+2)")` |
| `run_sysadmin_command` | System command | `run_sysadmin_command(command="df -h")` |
| `get_system_status` | System status | `get_system_status()` |
| `get_service_status` | Service status | `get_service_status(service_name="ollama")` |
| `get_recent_logs` | Recent logs | `get_recent_logs(lines=20)` |
| `store_user_preference` | Save preference | `store_user_preference(user_id="U123", key="lang", value="pt")` |
| `get_user_preference` | Get preference | `get_user_preference(user_id="U123", key="lang")` |
| `store_important_fact` | Store fact | `store_important_fact(fact="User likes Python", category="tech")` |
| `search_important_facts` | Search facts | `search_important_facts(query="Python")` |
| `switch_model` | Switch LLM | `switch_model(model_name="tinyllama")` |
| `get_available_models` | List models | `get_available_models()` |
| `get_current_model` | Current model | `get_current_model()` |

### Security Features

- **Command Whitelist**: Only safe system commands are allowed
- **Dangerous Pattern Blocking**: Blocks rm, sudo, chmod, etc.
- **Output Truncation**: Large outputs are truncated to prevent overflow
- **Argument Validation**: All tool arguments are validated
- **Thread Safety**: Memory operations use async locks
- **SQL Injection Prevention**: All database queries use parameterized queries

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Slack API                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      agent.py                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Memory    │  │     LLM     │  │    Tools    │         │
│  │  (async)    │  │  (Ollama)   │  │  (40+)      │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Smart     │  │   Long-term │  │  Scheduler  │         │
│  │  Routing    │  │   Memory    │  │  (APScheduler)│        │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│  DuckDuckGo │ OpenWeather │ Giphy │ GitHub │ Reddit         │
└─────────────────────────────────────────────────────────────┘
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_memory.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Test Coverage

| Module | Tests |
|--------|-------|
| `memory.py` | Memory limit, system prompt preservation, thread safety |
| `agent.py` | MAX_ITERATIONS fallback, argument parsing |
| `ollama_client.py` | Smart routing, no duplicate keywords |
| `tools.py` | Unknown tool handling, argument validation |
| `scheduler.py` | Interval parsing, recurrence formats |
| `long_term_memory.py` | User isolation, SQL injection prevention |
| `config.py` | Environment validation, type coercion |

---

## Português

### Visão Geral

Nordic-Claw é um bot do Slack que usa Ollama (LLM local) como cérebro. Possui pesquisa web, extração de conteúdo, geração de posts, clima, tradução, notas, tarefas agendadas, busca de vagas, geração de imagens, execução Python, administração de sistema e memória de longo prazo.

### Funcionalidades

| Funcionalidade | Descrição |
|----------------|------------|
| **Pesquisa Web** | Pesquisa na internet via DuckDuckGo com tratamento de rate limit |
| **Extração de Conteúdo** | Extrai texto limpo de qualquer URL |
| **Posts de Blog** | Gera posts em Markdown |
| **Clima** | Clima atual de qualquer cidade (OpenWeatherMap) |
| **Tradução** | Traduz para 12+ idiomas (API MyMemory - gratuito) |
| **Notas** | Salvar, recuperar, listar e deletar notas |
| **Mensagens Diretas** | Enviar DMs para usuários do Slack |
| **Lembretes** | Lembretes únicos enviados via DM (1min a 7 dias) |
| **GIFs** | Buscar e compartilhar GIFs via Giphy |
| **GitHub** | Ver atividade de repositórios (PRs, issues) |
| **Reddit** | Ver posts de subreddits ou buscar no Reddit |
| **Tarefas Agendadas** | Agendar tarefas recorrentes (diárias, horárias, interval) |
| **Caça de Vagas** | Busca automática de vagas com scoring e persistência |
| **Geração de Imagens** | Gerar imagens a partir de texto (Pollinations.ai) |
| **Execução Python** | Executar código Python seguro no VPS |
| **Administração de Sistema** | Executar comandos seguros de diagnóstico |
| **Memória de Longo Prazo** | Armazenar e recuperar preferências e fatos |
| **Troca de Modelo** | Trocar modelos LLM dinamicamente |
| **Roteamento Inteligente** | Rotear automaticamente consultas simples para modelos rápidos |

### Pré-requisitos

- Python 3.10+
- Ollama instalado e rodando (`ollama serve`)
- Modelo baixado: `ollama pull llama3.2:3b`

### ⚠️ Aviso de Segurança

**NUNCA commite o arquivo `.env` para o GitHub!**

Seu arquivo `.env` contém credenciais sensíveis:
- `SLACK_BOT_TOKEN`
- `SLACK_APP_TOKEN`
- `OPENWEATHER_API_KEY`
- `GIPHY_API_KEY`
- `GITHUB_TOKEN`

Este repositório usa `.gitignore` para excluir `.env`, mas sempre verifique antes de fazer push:
```bash
# Verifique se .env está no git status - NÃO deve estar!
git status
# Se .env aparecer, execute: git restore .env
```

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
OLLAMA_NUM_CTX=4096
OLLAMA_TIMEOUT=120

# APIs Opcionais
OPENWEATHER_API_KEY=sua-chave-api
GIPHY_API_KEY=sua-chave-giphy
GITHUB_TOKEN=seu-token-github

# Memória e Performance
MAX_MEMORY=10
MAX_ITERATIONS=3

# Roteamento Inteligente
SMART_ROUTING_ENABLED=true
FAST_MODEL=tinyllama

# Caça de Vagas (queries personalizadas opcionais)
JOB_SCOUT_QUERIES=Product Designer remote|UX Designer Brazil|Localization Portuguese
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
| `web_search` | Pesquisa web | `web_search(query="últimas notícias de IA")` |
| `fetch_webpage` | Extrair conteúdo de URL | `fetch_webpage(url="https://exemplo.com")` |
| `get_weather` | Clima atual | `get_weather(city="São Paulo", units="celsius")` |
| `translate_text` | Tradução | `translate_text(text="Olá", target_lang="english")` |
| `save_note` | Salvar nota | `save_note(key="ideias", content="Construir um bot...")` |
| `get_note` | Pegar nota | `get_note(key="ideias")` |
| `list_notes` | Listar notas | `list_notes()` |
| `delete_note` | Deletar nota | `delete_note(key="ideias")` |
| `send_dm` | Enviar DM | `send_dm(user_id="U123456", message="Olá!")` |
| `set_reminder` | Lembrete | `set_reminder(text="Reunião", minutes=30, user_id="U123")` |
| `search_gif` | Buscar GIFs | `search_gif(query="feliz", limit=5)` |
| `get_github_activity` | Atividade GitHub | `get_github_activity(repo="owner/repo", days=7)` |
| `scrape_reddit` | Posts do subreddit | `scrape_reddit(subreddit="brasil", sort="hot", limit=10)` |
| `search_reddit` | Buscar no Reddit | `search_reddit(query="dicas python", limit=10)` |
| `schedule_action` | Agendar tarefa | `schedule_action(prompt="Notícias", recurrence="todo dia às 9h", channel="C123")` |
| `search_jobs` | Caçar vagas | `search_jobs()` |
| `list_jobs` | Listar vagas salvas | `list_jobs(status="new", limit=10)` |
| `mark_job_applied` | Marcar como candidatada | `mark_job_applied(job_id="abc123")` |
| `get_job_stats` | Estatísticas de vagas | `get_job_stats()` |
| `generate_image` | Gerar imagem | `generate_image(prompt="um gato na praia", width=512, height=512)` |
| `execute_python_code` | Executar Python | `execute_python_code(code="print(2+2)")` |
| `run_sysadmin_command` | Comando de sistema | `run_sysadmin_command(command="df -h")` |
| `get_system_status` | Status do sistema | `get_system_status()` |
| `get_service_status` | Status de serviço | `get_service_status(service_name="ollama")` |
| `get_recent_logs` | Logs recentes | `get_recent_logs(lines=20)` |
| `store_user_preference` | Salvar preferência | `store_user_preference(user_id="U123", key="lang", value="pt")` |
| `get_user_preference` | Obter preferência | `get_user_preference(user_id="U123", key="lang")` |
| `store_important_fact` | Armazenar fato | `store_important_fact(fact="Usuário gosta de Python", category="tech")` |
| `search_important_facts` | Buscar fatos | `search_important_facts(query="Python")` |
| `switch_model` | Trocar LLM | `switch_model(model_name="tinyllama")` |
| `get_available_models` | Listar modelos | `get_available_models()` |
| `get_current_model` | Modelo atual | `get_current_model()` |

### Segurança

- **Whitelist de Comandos**: Apenas comandos seguros são permitidos
- **Bloqueio de Padrões Perigosos**: Bloqueia rm, sudo, chmod, etc.
- **Truncamento de Output**: Outputs grandes são truncados para evitar overflow
- **Validação de Argumentos**: Todos os argumentos são validados
- **Thread Safety**: Operações de memória usam locks assíncronos
- **Prevenção de SQL Injection**: Todas as queries usam parâmetros

### Testes

```bash
# Rodar todos os testes
pytest tests/ -v

# Rodar arquivo de teste específico
pytest tests/test_memory.py -v

# Rodar com cobertura
pytest tests/ --cov=. --cov-report=html
```

### Cobertura de Testes

| Módulo | Testes |
|--------|--------|
| `memory.py` | Limite de memória, preservação do system prompt, thread safety |
| `agent.py` | Fallback de MAX_ITERATIONS, parsing de argumentos |
| `ollama_client.py` | Smart routing, sem keywords duplicados |
| `tools.py` | Tratamento de ferramenta desconhecida, validação de argumentos |
| `scheduler.py` | Parsing de intervalo, formatos de recorrência |
| `long_term_memory.py` | Isolamento de usuário, prevenção de SQL injection |
| `config.py` | Validação de ambiente, coerção de tipos |

---

## Project Structure

```
a1gente/
├── agent.py              # Main entry point
├── config.py             # Configuration management with validation
├── memory.py             # Conversation memory (async, thread-safe)
├── ollama_client.py      # Ollama API client with smart routing
├── scheduler.py          # Task scheduler (APScheduler)
├── tools.py              # Tool definitions (40+ tools)
├── weather.py            # Weather tool
├── translate.py          # Translation tool
├── notes.py              # Notes storage tool
├── reminders.py          # One-time reminders
├── giphy.py              # GIF search tool
├── github_tools.py       # GitHub activity tool
├── reddit_tools.py       # Reddit scraping tool
├── web_utils.py          # Web fetching utilities
├── sysadmin_tools.py     # System administration tools
├── image_gen.py          # Image generation tool
├── job_scout.py          # Job hunting tool
├── long_term_memory.py   # User preferences and facts storage
├── model_manager.py      # Model switching
├── requirements.txt      # Dependencies
├── .env.example          # Environment template
├── tests/                # Test suite
│   ├── test_memory.py
│   ├── test_agent_max_iterations.py
│   ├── test_ollama_routing.py
│   ├── test_long_term_memory.py
│   ├── test_scheduler.py
│   └── test_tools.py
├── install.sh            # Installation script
├── update.sh             # Update script
└── uninstall.sh          # Uninstallation script
```

## Recent Changes

### Bug Fixes
- **Memory**: Fixed system prompt preservation during trim, added thread safety with async locks
- **Config**: Added startup validation warnings for missing environment variables
- **Tools**: Fixed argument parsing for JSON strings, added unknown tool error handling
- **Scheduler**: Fixed interval parsing (interval_30m now correctly uses minutes)
- **Reddit**: Added result limit clamping (1-25), network error handling
- **GitHub**: Added rate limit handling, repository not found errors
- **Image Gen**: Added timeout handling, proper error messages
- **Job Scout**: Added deduplication via seen_jobs.json, configurable queries

### New Features
- **Smart Routing**: Automatically routes simple queries to fast models
- **Long-term Memory**: Store and retrieve user preferences and facts
- **Job Scout**: Automatic job hunting with scoring and Slack notifications
- **Python Execution**: Execute safe Python code on the VPS
- **System Admin**: Run diagnostic commands safely
- **Image Generation**: Generate images from text prompts

### Security Improvements
- **Command Whitelist**: sysadmin_tools only allows safe commands
- **Argument Validation**: All tools validate required parameters
- **Output Truncation**: Prevents context overflow
- **SQL Injection Prevention**: Parameterized queries in long_term_memory

## License

MIT License - See LICENSE file for details.