import os
import json
import asyncio
import httpx
import logging
import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import pytz
import dateparser
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from dotenv import load_dotenv
from duckduckgo_search import DDGS

# Configurações de Log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# --- CONFIGURAÇÕES ---
# Carrega variáveis do arquivo .env
load_dotenv()

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
SLACK_BOT_USER_ID = os.environ.get("SLACK_BOT_USER_ID")
# Suporte a OLLAMA_URL ou OLLAMA_BASE_URL
OLLAMA_URL = os.environ.get("OLLAMA_URL") or os.environ.get("OLLAMA_BASE_URL") or "http://localhost:11434"
# Suporte a MODEL_NAME ou MODEL
MODEL_NAME = os.environ.get("MODEL_NAME") or os.environ.get("MODEL") or "llama3.2:3b"

# --- CONFIGURAÇÕES DE PERSISTÊNCIA ---
# Caminho para arquivar tarefas agendadas
SCHEDULED_TASKS_FILE = "scheduled_tasks.json"

def load_scheduled_tasks() -> List[Dict[str, Any]]:
    if os.path.exists(SCHEDULED_TASKS_FILE):
        try:
            with open(SCHEDULED_TASKS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar tarefas agendadas: {e}")
    return []

def save_scheduled_tasks(tasks: List[Dict[str, Any]]):
    try:
        with open(SCHEDULED_TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erro ao salvar tarefas agendadas: {e}")

# --- MEMÓRIA ---
# Dicionário para armazenar o histórico de mensagens por canal/usuário
memory: Dict[str, List[Dict[str, Any]]] = {}
MAX_MEMORY = 10

def update_memory(channel_id: str, role: str, content: str, tool_calls: Optional[List] = None):
    if channel_id not in memory:
        memory[channel_id] = []
    
    msg = {"role": role, "content": content}
    if tool_calls:
        msg["tool_calls"] = tool_calls
        
    memory[channel_id].append(msg)
    
    # Mantém os últimos N mensagens
    if len(memory[channel_id]) > MAX_MEMORY:
        memory[channel_id] = memory[channel_id][-MAX_MEMORY:]

# --- FERRAMENTAS (TOOLS) ---

async def read_slack_message(text: str) -> str:
    """Lê o texto da mensagem do Slack e devolve para o LLM."""
    return f"Mensagem lida: {text}"

async def write_blog_post(title: str, content: str) -> str:
    """Gera um post de blog em markdown, com estrutura de seções, subtítulos, etc."""
    blog_md = f"# {title}\n\n{content}\n\n---\n*Post gerado automaticamente pelo Agente AI*"
    return f"Blog post gerado:\n\n{blog_md}"

async def web_search(query: str) -> str:
    """Pesquisa no DuckDuckGo e retorna os resultados principais com links."""
    try:
        results_text = []
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)
            for r in results:
                results_text.append(f"- {r['title']}: {r['href']}\n  {r['body']}")
        
        if not results_text:
            return "Nenhum resultado encontrado para a pesquisa."
        
        return "\n\n".join(results_text)
    except Exception as e:
        logger.error(f"Erro na pesquisa DuckDuckGo: {e}")
        return f"Erro ao pesquisar: {str(e)}"

async def fetch_webpage(url: str) -> str:
    """Faz GET num site e retorna o texto limpo."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            soup = BeautifulSoup(response.text, 'html.parser')
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text(separator=' ')
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = '\n'.join(chunk for chunk in chunks if chunk)
            return clean_text[:2000]
    except Exception as e:
        return f"Erro ao acessar a URL {url}: {str(e)}"

async def summarize_text(text: str) -> str:
    """Tool de fachada para resumo."""
    return f"Resumo solicitado para: {text[:100]}..."

async def reply_to_slack(channel: str, message: str) -> str:
    """Envia mensagem de volta ao Slack."""
    try:
        await app.client.chat_postMessage(channel=channel, text=str(message))
        return "Mensagem enviada com sucesso ao Slack."
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem ao Slack: {e}")
        return f"Erro ao enviar mensagem ao Slack: {str(e)}"

async def schedule_action(prompt: str, recurrence: str, channel: str) -> str:
    """Agenda uma ação recorrente."""
    try:
        tasks = load_scheduled_tasks()
        new_task = {
            "id": f"task_{int(datetime.now().timestamp())}",
            "prompt": prompt,
            "recurrence": recurrence,
            "channel": channel,
            "created_at": datetime.now().isoformat()
        }
        tasks.append(new_task)
        save_scheduled_tasks(tasks)
        add_task_to_scheduler(new_task)
        
        msg = f"✅ *Agendado com sucesso!*\n\n• *Ação*: {prompt}\n• *Frequência*: {recurrence}\n• *Canal*: <#{channel}>"
        await app.client.chat_postMessage(channel=channel, text=msg)
        return f"Tarefa agendada e confirmada: {msg}"
    except Exception as e:
        logger.error(f"Erro ao agendar tarefa: {e}")
        return f"Erro ao agendar tarefa: {str(e)}"

# Ferramentas registradas
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_slack_message",
            "description": "Lê o texto original da mensagem recebida.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_blog_post",
            "description": "Cria um post de blog em Markdown.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["title", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_webpage",
            "description": "Busca o conteúdo textual de uma URL.",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_text",
            "description": "Solicita um resumo.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reply_to_slack",
            "description": "Envia uma resposta para o Slack.",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel": {"type": "string"},
                    "message": {"type": "string"}
                },
                "required": ["channel", "message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Pesquisa na internet usando DuckDuckGo.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_action",
            "description": "Agenda uma tarefa periódica (ex: todo dia às 9h).",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "O que fazer na execução."},
                    "recurrence": {"type": "string", "description": "Regra (ex: todo dia às 9h)."},
                    "channel": {"type": "string", "description": "ID do canal Slack (C...)."}
                },
                "required": ["prompt", "recurrence", "channel"]
            }
        }
    }
]

# --- SCHEDULER ---
scheduler = AsyncIOScheduler()

def add_task_to_scheduler(task: Dict[str, Any]):
    try:
        if "todo dia" in task["recurrence"].lower():
            match = re.search(r'(\d{1,2})[h:](\d{0,2})', task["recurrence"])
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2)) if match.group(2) else 0
                scheduler.add_job(
                    run_scheduled_task, 'cron', hour=hour, minute=minute,
                    args=[task], id=task["id"], replace_existing=True
                )
                logger.info(f"Tarefa {task['id']} agendada: {hour:02d}:{minute:02d} diariamente.")
        else:
            scheduler.add_job(
                run_scheduled_task, 'interval', minutes=60,
                args=[task], id=task["id"], replace_existing=True
            )
    except Exception as e:
        logger.error(f"Erro ao adicionar tarefa ao scheduler: {e}")

async def run_scheduled_task(task: Dict[str, Any]):
    logger.info(f"Executando tarefa agendada: {task['prompt']}")
    await run_agent(task["channel"], f"TAREFA AGENDADA: {task['prompt']}")

# --- OLLAMA API ---

async def call_ollama(messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    url = f"{OLLAMA_URL}/api/chat"
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {"num_ctx": 4096}
    }
    if tools:
        payload["tools"] = tools

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=300.0)
            if response.status_code != 200:
                return {"message": {"role": "assistant", "content": f"Erro Ollama: {response.text}"}}
            return response.json()
        except Exception as e:
            return {"message": {"role": "assistant", "content": f"Erro Conexão: {str(e)}"}}

# --- LÓGICA DO AGENTE ---

async def run_agent(channel_id: str, user_text: str):
    # System Instruction repetida para garantir obediência do modelo 3B
    instructions = (
        "Você é o Nordic-Claw, assistente Slack. REGRAS:\n"
        "1. Use tools diretamente via 'tool_calls' quando necessário. NÃO mostre JSON no chat.\n"
        f"2. Se for agendar para este canal, o ID é '{channel_id}'.\n"
        "3. Responda sempre em Português."
    )

    if channel_id not in memory:
        update_memory(channel_id, "system", instructions)
    
    update_memory(channel_id, "user", user_text)
    
    for i in range(5):
        logger.info(f"Iteração {i+1} - Canal: {channel_id}")
        response_data = await call_ollama(memory[channel_id], tools=TOOLS)
        message = response_data.get("message", {})
        content = message.get("content", "")
        tool_calls = message.get("tool_calls", [])
        
        # Fallback para JSON manual no conteúdo
        if not tool_calls and "{" in content and "}" in content:
            try:
                j_match = re.search(r'\{.*\}', content, re.DOTALL)
                if j_match:
                    manual = json.loads(j_match.group(0))
                    if "name" in manual:
                        tool_calls = [{
                            "function": {
                                "name": manual["name"],
                                "arguments": manual.get("parameters", manual.get("arguments", {}))
                            }
                        }]
                        content = content.replace(j_match.group(0), "").strip()
            except:
                pass

        memory[channel_id].append({"role": "assistant", "content": content, "tool_calls": tool_calls})
        
        if not tool_calls:
            if content:
                await app.client.chat_postMessage(channel=channel_id, text=content)
            break
        
        for tc in tool_calls:
            fn = tc["function"]["name"]
            args = tc["function"]["arguments"]
            logger.info(f"Ferramenta: {fn}")
            
            res = ""
            try:
                if fn == "read_slack_message": res = await read_slack_message(**args)
                elif fn == "write_blog_post": res = await write_blog_post(**args)
                elif fn == "fetch_webpage": res = await fetch_webpage(**args)
                elif fn == "summarize_text": res = await summarize_text(**args)
                elif fn == "reply_to_slack": res = await reply_to_slack(**args)
                elif fn == "web_search": res = await web_search(**args)
                elif fn == "schedule_action": res = await schedule_action(**args)
                else: res = f"Erro: {fn} não encontrada."
            except Exception as e:
                res = f"Erro {fn}: {str(e)}"
            
            memory[channel_id].append({"role": "tool", "content": str(res)})

# --- SLACK ---

app = AsyncApp(token=SLACK_BOT_TOKEN)

@app.event("app_mention")
async def handle_mentions(event, say):
    text = event.get("text", "").replace(f"<@{SLACK_BOT_USER_ID}>", "").strip()
    await run_agent(event.get("channel"), text)

@app.event("message")
async def handle_messages(event, say):
    if event.get("channel_type") == "im":
        await run_agent(event.get("channel"), event.get("text", ""))

async def main():
    scheduler.start()
    for t in load_scheduled_tasks():
        add_task_to_scheduler(t)
    handler = AsyncSocketModeHandler(app, SLACK_APP_TOKEN)
    await handler.start_async()

if __name__ == "__main__":
    asyncio.run(main())
