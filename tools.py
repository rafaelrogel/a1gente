from typing import List, Dict, Any, Optional
import logging
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_slack_message",
            "description": "Reads the original message text. Use this first to process any user message.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_blog_post",
            "description": "Creates a blog post in Markdown format with title and content sections.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["title", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_webpage",
            "description": "Fetches and extracts clean text content from a URL.",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_text",
            "description": "Requests a summary of the provided text.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reply_to_slack",
            "description": "Sends a reply message to a Slack channel.",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel": {"type": "string"},
                    "message": {"type": "string"},
                },
                "required": ["channel", "message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Searches the internet using DuckDuckGo. Returns real results with titles, URLs, and descriptions.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_action",
            "description": "Schedules a recurring task (e.g., daily at 9am).",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "What to execute when the task runs.",
                    },
                    "recurrence": {
                        "type": "string",
                        "description": "Recurrence rule (e.g., 'todo dia às 9h').",
                    },
                    "channel": {
                        "type": "string",
                        "description": "Slack channel ID (C...).",
                    },
                },
                "required": ["prompt", "recurrence", "channel"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Gets current weather for a city. Requires OPENWEATHER_API_KEY env variable.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name (e.g., 'São Paulo', 'New York').",
                    },
                    "units": {
                        "type": "string",
                        "description": "Temperature units: 'celsius' or 'fahrenheit'. Default: celsius.",
                    },
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "translate_text",
            "description": "Translates text from English to the target language using MyMemory API (free).",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to translate (in English).",
                    },
                    "target_lang": {
                        "type": "string",
                        "description": "Target language name or code (e.g., 'portuguese', 'pt', 'spanish', 'es').",
                    },
                },
                "required": ["text", "target_lang"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_note",
            "description": "Saves a note with a key for later retrieval.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Unique identifier for the note (e.g., 'project-ideas', 'todo-list').",
                    },
                    "content": {"type": "string", "description": "Content to save."},
                },
                "required": ["key", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_note",
            "description": "Retrieves a previously saved note by its key.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The key used when saving the note.",
                    },
                },
                "required": ["key"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_notes",
            "description": "Lists all saved note keys.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_note",
            "description": "Deletes a note by its key.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The key of the note to delete.",
                    },
                },
                "required": ["key"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_dm",
            "description": "Sends a direct message to a Slack user by their user ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Slack user ID (e.g., 'U12345678').",
                    },
                    "message": {"type": "string", "description": "Message to send."},
                },
                "required": ["user_id", "message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_reminder",
            "description": "Sets a one-time reminder. Bot will DM you after the specified minutes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Reminder text."},
                    "minutes": {
                        "type": "integer",
                        "description": "Minutes until reminder (1-10080).",
                    },
                    "user_id": {
                        "type": "string",
                        "description": "Your Slack user ID to receive the DM.",
                    },
                },
                "required": ["text", "minutes", "user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_gif",
            "description": "Searches for GIFs using Giphy.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for GIF."},
                    "limit": {
                        "type": "integer",
                        "description": "Max GIFs to return (1-10). Default: 5.",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_github_activity",
            "description": "Gets recent GitHub activity for a repository (PRs and issues).",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in format 'owner/repo' (e.g., 'rafaelrogel/a1gente').",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Days to look back. Default: 7.",
                    },
                },
                "required": ["repo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "scrape_reddit",
            "description": "Gets recent posts from a subreddit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subreddit": {
                        "type": "string",
                        "description": "Subreddit name without 'r/' (e.g., 'programming', 'brasil').",
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort by: 'hot', 'new', 'top'. Default: 'hot'.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of posts (1-25). Default: 10.",
                    },
                },
                "required": ["subreddit"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_reddit",
            "description": "Searches all of Reddit for posts matching a query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query."},
                    "limit": {
                        "type": "integer",
                        "description": "Number of results (1-25). Default: 10.",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "switch_model",
            "description": "Switches the LLM model. Clears conversation context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Model name: llama3.2:3b, tinyllama, qwen2.5:1.5b, granite3.1-moe",
                    },
                },
                "required": ["model_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_available_models",
            "description": "Lists all available models that can be switched to.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_model",
            "description": "Gets the currently active model.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "show_features",
            "description": "Shows all available features and commands.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_image",
            "description": "Generates an image from a text prompt using free AI image generation service.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Text description of the image to generate (e.g., 'a cat wearing sunglasses on a beach')",
                    },
                    "width": {
                        "type": "integer",
                        "description": "Image width in pixels (default: 512, min: 64, max: 1024)",
                    },
                    "height": {
                        "type": "integer",
                        "description": "Image height in pixels (default: 512, min: 64, max: 1024)",
                    },
                },
                "required": ["prompt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_sysadmin_command",
            "description": "Executes a safe system command on the VPS for diagnostics (disk, memory, uptime, git status, etc).",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The system command to run (e.g., 'df -h', 'free -m', 'uptime', 'git status')",
                    },
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_status",
            "description": "Gets a comprehensive system status report (hostname, uptime, CPU, memory, disk, load).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_service_status",
            "description": "Gets the status of a specific system service.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "Name of the service to check (e.g., 'a1gente', 'ollama', 'docker')",
                    },
                },
                "required": ["service_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_recent_logs",
            "description": "Gets recent logs from the a1gente service.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lines": {
                        "type": "integer",
                        "description": "Number of log lines to retrieve (default: 20, max: 100)",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_git_status",
            "description": "Gets the git status, recent commits, and current branch of the project.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "store_user_preference",
            "description": "Stores a user preference for long-term memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The Slack user ID",
                    },
                    "key": {
                        "type": "string",
                        "description": "Preference key (e.g., 'language', 'timezone', 'name')",
                    },
                    "value": {
                        "type": "string",
                        "description": "Preference value",
                    },
                },
                "required": ["user_id", "key", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_preference",
            "description": "Retrieves a stored user preference.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The Slack user ID",
                    },
                    "key": {
                        "type": "string",
                        "description": "Preference key to retrieve",
                    },
                },
                "required": ["user_id", "key"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "store_important_fact",
            "description": "Stores an important fact for long-term reference.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fact": {
                        "type": "string",
                        "description": "The important fact to store",
                    },
                    "category": {
                        "type": "string",
                        "description": "Category for the fact (e.g., 'project', 'team', 'technical')",
                    },
                },
                "required": ["fact"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_important_facts",
            "description": "Searches stored important facts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for facts",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_daily_report",
            "description": "Schedules an automated daily report to be posted in a Slack channel.",
            "parameters": {
                "type": "object",
                "properties": {
                    "report_type": {
                        "type": "string",
                        "description": "Type of report: 'daily_briefing', 'morning_news', 'evening_summary', 'weekly_report'",
                    },
                    "channel": {
                        "type": "string",
                        "description": "Slack channel ID to post the report",
                    },
                    "time": {
                        "type": "string",
                        "description": "Time to post the report (e.g., '09:00', '18h30')",
                    },
                },
                "required": ["report_type", "channel"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_available_reports",
            "description": "Lists all available automated report types that can be scheduled.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "execute_python_code",
            "description": "Executes simple Python code safely on the VPS. Supports math, data processing, text manipulation, and more. Blocks dangerous operations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute (max 5000 chars). Can use: math, json, datetime, random, re, collections, itertools, statistics, etc.",
                    },
                },
                "required": ["code"],
            },
        },
    },
]


def get_features_message() -> str:
    return """🤖 *Olá! Eu sou o Nordic-Claw!*

Aqui estão todas as minhas funcionalidades e como me usar:

━━━━━━━━━━━━━━━━━━━━━━

🔍 *PESQUISA E INFORMAÇÃO*
• `pesquise sobre [tema]` - Buscar notícias e informações
• `mostre posts do reddit [subreddit]` - Ver posts do Reddit
• `busque no reddit [termo]` - Buscar no Reddit

🌐 *WEB*
• `busque [URL]` - Extrair conteúdo de uma página
• `resuma [texto ou URL]` - Resumir conteúdo

🌤️ *CLIMA*
• `qual o clima em [cidade]?` - Ver previsão do tempo

🌐 *TRADUÇÃO*
• `traduza "[texto]" para [idioma]` - Traduzir texto

📝 *NOTAS*
• `salve uma nota: [chave], conteúdo: [texto]` - Salvar nota
• `veja minha nota [chave]` - Ver nota
• `liste minhas notas` - Listar todas
• `delete nota [chave]` - Deletar nota

⏰ *LEMBRETES*
• `me lembre de [texto] em [X] minutos` - Definir lembrete

🎬 *GIFS*
• `procure um gif de [termo]` - Buscar GIF

📊 *GITHUB*
• `mostre atividade do github [owner/repo]` - Ver PRs e issues

🖼️ *GERAÇÃO DE IMAGENS*
• `gere uma imagem: [descrição] [largura X altura]` - Gerar imagem (ex: `gere uma imagem: gato de óculos de sol na praia 512x512`)

🔄 *MODELOS DE IA*
• `mude para [modelo]` - Trocar modelo (tinyllama, granite3.1-moe, qwen2.5:1.5b, llama3.2:3b)
• `qual modelo estamos usando?` - Ver modelo atual
• `liste os modelos disponíveis` - Ver todos
• *Roteamento inteligente*: Uso automático de modelo rápido para perguntas simples

🖥️ *ADMINISTRAÇÃO DO SISTEMA*
• `status do sistema` - Ver status completo (CPU, RAM, disco, uptime)
• `status do serviço [nome]` - Ver status de um serviço (ex: a1gente, ollama, docker)
• `execute comando [comando]` - Executar comando seguro (ex: df -h, free -m, uptime)
• `logs recentes [N]` - Ver logs recentes do serviço (ex: logs recentes 20)
• `status do git` - Ver status do git, branch e commits recentes

💻 *EXECUÇÃO DE CÓDIGO PYTHON*
• `execute python: [codigo]` - Executar codigo Python simples no VPS
• Exemplos: `execute python: print(2 + 2)`, `execute python: import math; print(math.pi)`, `execute python: print([x**2 for x in range(10)])`
• Suporta: math, json, datetime, random, re, collections, itertools, statistics, string
• Bloqueado: os, subprocess, socket, eval, exec, open, import

🧠 *MEMÓRIA DE LONGO PRAZO*
• `lembre que [fato]` - Armazenar fato importante para referência futura
• `busque na memória [termo]` - Buscar fatos armazenados
• `salve minha preferência [chave] = [valor]` - Salvar preferência pessoal
• `qual minha preferência [chave]?` - Ver preferência salva

📅 *RELATÓRIOS AUTOMÁTICOS*
• `agende relatório [tipo] às [hora]` - Agendar relatório automático
• `tipos de relatório` - Ver tipos disponíveis (daily_briefing, morning_news, evening_summary, weekly_report)
• `agende daily_briefing todo dia às 09:00` - Exemplo de agendamento

💬 *OUTROS*
• `crie um post de blog: título [X], conteúdo [Y]`
• `envie DM para [user_id]: [mensagem]`

━━━━━━━━━━━━━━━━━━━━━━

💡 *Dica:* Seja específico para melhores resultados!"""


async def read_slack_message(text: str) -> str:
    return f"Mensagem lida: {text}"


async def write_blog_post(title: str, content: str) -> str:
    blog_md = (
        f"# {title}\n\n{content}\n\n---\n*Post gerado automaticamente pelo Agente AI*"
    )
    return f"Blog post gerado:\n\n{blog_md}"


async def web_search(query: str) -> str:
    try:
        results_text = []
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=10)
            for r in results:
                results_text.append(
                    f"TITULO: {r['title']}\nURL: {r['href']}\nDESCRICAO: {r['body']}"
                )

        if not results_text:
            return "NENHUM_RESULTADO: Nenhum resultado encontrado para a pesquisa."

        return "RESULTADOS_REAIS:\n" + "\n---\n".join(results_text)
    except Exception as e:
        logger.error(f"Erro na pesquisa DuckDuckGo: {e}")
        return f"ERRO_PESQUISA: Erro ao pesquisar: {str(e)}"


async def summarize_text(text: str) -> str:
    return f"Resumo solicitado para: {text[:100]}..."


async def execute_tool(name: str, args: Dict[str, Any], app=None) -> str:
    if name == "read_slack_message":
        return await read_slack_message(**args)
    elif name == "write_blog_post":
        return await write_blog_post(**args)
    elif name == "fetch_webpage":
        from web_utils import fetch_webpage

        return await fetch_webpage(**args)
    elif name == "summarize_text":
        return await summarize_text(**args)
    elif name == "reply_to_slack":
        if app:
            await app.client.chat_postMessage(
                channel=args["channel"], text=str(args["message"])
            )
            return "Mensagem enviada com sucesso ao Slack."
        return "Erro: app não disponível"
    elif name == "web_search":
        return await web_search(**args)
    elif name == "schedule_action":
        from agent import schedule_action

        return await schedule_action(**args)
    elif name == "get_weather":
        from weather import get_weather

        return await get_weather(**args)
    elif name == "translate_text":
        from translate import translate_text

        return await translate_text(**args)
    elif name == "save_note":
        from notes import save_note

        return await save_note(**args)
    elif name == "get_note":
        from notes import get_note

        return await get_note(**args)
    elif name == "list_notes":
        from notes import list_notes

        return await list_notes()
    elif name == "delete_note":
        from notes import delete_note

        return await delete_note(**args)
    elif name == "send_dm":
        if app:
            try:
                result = await app.client.conversations_open(users=args["user_id"])
                channel_id = result["channel"]["id"]
                await app.client.chat_postMessage(
                    channel=channel_id, text=str(args["message"])
                )
                return f"Mensagem enviada para usuário {args['user_id']}"
            except Exception as e:
                logger.error(f"Erro ao enviar DM: {e}")
                return f"ERRO ao enviar DM: {str(e)}"
        return "Erro: app não disponível"
    elif name == "set_reminder":
        from reminders import set_reminder

        return await set_reminder(**args)
    elif name == "search_gif":
        from giphy import search_gif

        return await search_gif(**args)
    elif name == "get_github_activity":
        from github_tools import get_github_activity

        return await get_github_activity(**args)
    elif name == "scrape_reddit":
        from reddit_tools import scrape_reddit

        return await scrape_reddit(**args)
    elif name == "search_reddit":
        from reddit_tools import search_reddit

        return await search_reddit(**args)
    elif name == "switch_model":
        from model_manager import switch_model

        return switch_model(**args)
    elif name == "get_available_models":
        from model_manager import get_available_models

        return "Modelos disponíveis: " + ", ".join(get_available_models())
    elif name == "get_current_model":
        from model_manager import get_current_model

        return f"Modelo atual: {get_current_model()}"
    elif name == "show_features":
        return get_features_message()
    elif name == "generate_image":
        from image_gen import generate_image

        return await generate_image(**args)
    elif name == "run_sysadmin_command":
        from sysadmin_tools import run_sysadmin_command

        return await run_sysadmin_command(**args)
    elif name == "get_system_status":
        from sysadmin_tools import get_system_status

        return await get_system_status()
    elif name == "get_service_status":
        from sysadmin_tools import get_service_status

        return await get_service_status(**args)
    elif name == "get_recent_logs":
        from sysadmin_tools import get_recent_logs

        return await get_recent_logs(**args)
    elif name == "get_git_status":
        from sysadmin_tools import get_git_status

        return await get_git_status()
    elif name == "store_user_preference":
        from long_term_memory import store_user_preference

        result = store_user_preference(**args)
        if result:
            return f"Preferencia armazenada com sucesso: {args.get('key')} = {args.get('value')}"
        return "Erro ao armazenar preferencia."
    elif name == "get_user_preference":
        from long_term_memory import get_user_preference

        value = get_user_preference(
            args.get("user_id"), args.get("key"), "Nao encontrada"
        )
        return f"Preferencia '{args.get('key')}': {value}"
    elif name == "store_important_fact":
        from long_term_memory import store_important_fact

        result = store_important_fact(
            args.get("fact"),
            args.get("category", "general"),
            args.get("source", "user"),
        )
        if result:
            return f"Fato importante armazenado: {args.get('fact')[:100]}"
        return "Erro ao armazenar fato."
    elif name == "search_important_facts":
        from long_term_memory import search_important_facts

        facts = search_important_facts(args.get("query", ""), 5)
        if facts:
            msg = "🔍 *Fatos Encontrados:*\n\n"
            for f in facts:
                msg += f"• {f['fact']} (categoria: {f['category']})\n"
            return msg
        return f"Nenhum fato encontrado para: {args.get('query', '')}"
    elif name == "schedule_daily_report":
        from scheduler import add_report_to_scheduler

        task = add_report_to_scheduler(
            args.get("report_type"),
            args.get("channel"),
            args.get("time"),
        )
        if task:
            return f"Relatorio agendado com sucesso!\n• Tipo: {task.get('report_type')}\n• Canal: {task.get('channel')}\n• Horario: {task.get('recurrence')}"
        return "Erro ao agendar relatorio."
    elif name == "list_available_reports":
        from scheduler import get_available_reports

        reports = get_available_reports()
        if reports:
            msg = "📋 *Relatórios Disponíveis:*\n\n"
            for r in reports:
                msg += f"• *{r['name']}*: {r['description']}\n  Horário padrão: {r['default_time']}\n\n"
            return msg
        return "Nenhum relatório disponível."
    elif name == "execute_python_code":
        from sysadmin_tools import execute_python_code

        return await execute_python_code(**args)
    else:
        return f"Erro: {name} não encontrada."
