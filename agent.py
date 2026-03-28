import os
import json
import asyncio
import httpx
import logging
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
        memory[channel_id] = [{"role": "system", "content": "Você é um assistente prestativo integrado ao Slack. Use as ferramentas disponíveis quando necessário."}]
    
    msg = {"role": role, "content": content}
    if tool_calls:
        msg["tool_calls"] = tool_calls
        
    memory[channel_id].append(msg)
    
    # Mantém a primeira mensagem (System) e as últimas N-1
    if len(memory[channel_id]) > MAX_MEMORY:
        system_msg = memory[channel_id][0]
        recent_msgs = memory[channel_id][-(MAX_MEMORY-1):]
        memory[channel_id] = [system_msg] + recent_msgs

# --- FERRAMENTAS (TOOLS) ---

async def read_slack_message(text: str) -> str:
    """Lê o texto da mensagem do Slack e devolve para o LLM."""
    return f"Mensagem lida: {text}"

async def write_blog_post(title: str, content: str) -> str:
    """Gera um post de blog em markdown, com estrutura de seções, subtítulos, etc."""
    blog_md = f"# {title}\n\n{content}\n\n---\n*Post gerado automaticamente pelo Agente AI*"
    # Aqui poderíamos salvar num arquivo, mas vamos retornar o texto
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
            # Remove scripts e estilos
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text(separator=' ')
            # Limpa espaços em branco
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = '\n'.join(chunk for chunk in chunks if chunk)
            return clean_text[:2000] # Limita a 2000 caracteres para não estourar contexto
    except Exception as e:
        return f"Erro ao acessar a URL {url}: {str(e)}"

async def summarize_text(text: str) -> str:
    """Resume um texto curto (placeholder para o LLM já saber que pode resumir)."""
    # Na verdade, o LLM vai resumir usando o contexto, mas a tool pode servir para processar chunks
    return f"Resumo solicitado para: {text[:100]}..."

async def reply_to_slack(channel: str, message: str) -> str:
    """Envia mensagem de volta ao Slack (usando o token do bot)."""
    try:
        # Garante que 'text' seja enviado para evitar avisos no SDK do Slack
        await app.client.chat_postMessage(channel=channel, text=str(message))
        return "Mensagem enviada com sucesso ao Slack."
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem ao Slack: {e}")
        return f"Erro ao enviar mensagem ao Slack: {str(e)}"

async def schedule_action(prompt: str, recurrence: str, channel: str) -> str:
    """Agenda uma ação recorrente para o agente realizar de forma autônoma."""
    try:
        # Tenta sanitizar o channel: se não começar com C ou D, o LLM pode ter passado o nome.
        # Mas para o scheduler funcionar, precisamos do ID.
        # Se formos chamados via Slack, o channel_id atual está disponível no contexto.
        # Por simplicidade, se o ID não parecer um canal Slack, avisamos.
        if not (channel.startswith("C") or channel.startswith("D")):
             logger.warning(f"O nome do canal '{channel}' pode não ser um ID válido do Slack.")

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
        
        # Adiciona ao scheduler ativo
        add_task_to_scheduler(new_task)
        
        msg = f"✅ *Agendado com sucesso!*\n\n• *Ação*: {prompt}\n• *Frequência*: {recurrence}\n• *Canal*: <#{channel}>"
        
        # Envia confirmação imediata ao Slack para garantir que o usuário saiba que funcionou
        await app.client.chat_postMessage(channel=channel, text=msg)
        
        return msg
    except Exception as e:
        logger.error(f"Erro ao agendar tarefa: {e}")
        return f"Erro ao agendar tarefa: {str(e)}"

# Definição das tools para o Ollama
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_slack_message",
            "description": "Lê o texto original da mensagem recebida para processamento.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "O texto da mensagem."}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_blog_post",
            "description": "Cria um post de blog estruturado em formato Markdown.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Título do post."},
                    "content": {"type": "string", "description": "Conteúdo principal do post."}
                },
                "required": ["title", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_webpage",
            "description": "Busca o conteúdo textual de uma URL pública.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "A URL completa do site."}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_text",
            "description": "Solicita um resumo de um texto longo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "O texto a ser resumido."}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reply_to_slack",
            "description": "Envia uma resposta final ou atualização para o canal do Slack.",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel": {"type": "string", "description": "O ID do canal do Slack."},
                    "message": {"type": "string", "description": "A mensagem a ser enviada."}
                },
                "required": ["channel", "message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Pesquisa na internet por informações em tempo real usando DuckDuckGo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "O termo de pesquisa."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_action",
            "description": "Agenda uma tarefa ou pesquisa periódica (ex: todo dia, toda segunda) e envia para o Slack.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "O que o agente deve fazer na execução (ex: 'Top 10 notícias de IA')."},
                    "recurrence": {"type": "string", "description": "Regra de recorrência em português (ex: 'todo dia às 9h')."},
                    "channel": {"type": "string", "description": "O ID do canal do Slack (EX: C0123456)."}
                },
                "required": ["prompt", "recurrence", "channel"]
            }
        }
    }
]

# --- BACKGROUND SCHEDULER ---

scheduler = AsyncIOScheduler()

def add_task_to_scheduler(task: Dict[str, Any]):
    """Adiciona uma tarefa ao scheduler baseada em regras de tempo simples."""
    try:
        # Simplificação: agenda para rodar em intervalos se for 'todo dia' ou algo similar
        # Em um app real, usaríamos cron triggers do APScheduler mais complexos
        # Aqui, vamos parsear 'todo dia às HH:MM'
        if "todo dia" in task["recurrence"].lower():
            # Extrai HH:MM do texto
            import re
            match = re.search(r'(\d{1,2})[h:](\d{0,2})', task["recurrence"])
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2)) if match.group(2) else 0
                scheduler.add_job(
                    run_scheduled_task,
                    'cron',
                    hour=hour,
                    minute=minute,
                    args=[task],
                    id=task["id"],
                    replace_existing=True
                )
                logger.info(f"Tarefa {task['id']} agendada para as {hour:02d}:{minute:02d} diariamente.")
        else:
            # Fallback para teste: a cada 60 minutos se não entender
            scheduler.add_job(
                run_scheduled_task,
                'interval',
                minutes=60,
                args=[task],
                id=task["id"],
                replace_existing=True
            )
    except Exception as e:
        logger.error(f"Erro ao adicionar tarefa ao scheduler: {e}")

async def run_scheduled_task(task: Dict[str, Any]):
    """Executa a tarefa agendada sem intervenção do usuário."""
    logger.info(f"Executando tarefa agendada: {task['prompt']}")
    await run_agent(task["channel"], f"TAREFA AGENDADA: {task['prompt']}")

# --- INTEGRAÇÃO OLLAMA ---

async def call_ollama(messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    url = f"{OLLAMA_URL}/api/chat"
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False
    }
    if tools:
        payload["tools"] = tools
        # Limita o contexto para 4096 tokens para acelerar o processamento em VPS lentas
        payload["options"] = {"num_ctx": 4096}

    async with httpx.AsyncClient() as client:
        try:
            # Aumentado para 300s (5 minutos) para evitar ReadTimeout em VPS lentas
            response = await client.post(url, json=payload, timeout=300.0) 
            if response.status_code != 200:
                logger.error(f"Ollama retornou erro {response.status_code}: {response.text}")
                return {"message": {"role": "assistant", "content": f"Erro do Ollama ({response.status_code}): {response.text}"}}
            
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao chamar Ollama: {type(e).__name__}: {e}")
            return {"message": {"role": "assistant", "content": f"Erro de conexão com Ollama: {str(e)}"}}

# --- LÓGICA DO AGENTE ---

async def run_agent(channel_id: str, user_text: str):
    # Inicializa memória se necessário
    if channel_id not in memory:
        update_memory(channel_id, "system", "Você é um assistente prestativo integrado ao Slack.")
    
    update_memory(channel_id, "user", user_text)
    
    # Loop de raciocínio (pensamento + tool use)
    for i in range(5):
        logger.info(f"Rodando iteração {i+1} do agente para o canal {channel_id}")
        response_data = await call_ollama(memory[channel_id], tools=TOOLS)
        message = response_data.get("message", {})
        
        # Adiciona resposta do assistente (com ou sem tool_calls) à memória
        memory[channel_id].append(message)
        
        tool_calls = message.get("tool_calls")
        if not tool_calls:
            if message.get("content"):
                await app.client.chat_postMessage(channel=channel_id, text=message["content"])
            break
                # Executa as ferramentas solicitadas
        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]
            
            logger.info(f"Executando ferramenta: {function_name}")
            
            result = ""
            try:
                if function_name == "read_slack_message":
                    result = await read_slack_message(**arguments)
                elif function_name == "write_blog_post":
                    result = await write_blog_post(**arguments)
                elif function_name == "fetch_webpage":
                    result = await fetch_webpage(**arguments)
                elif function_name == "summarize_text":
                    result = await summarize_text(**arguments)
                elif function_name == "reply_to_slack":
                    result = await reply_to_slack(**arguments)
                elif function_name == "web_search":
                    result = await web_search(**arguments)
                elif function_name == "schedule_action":
                    result = await schedule_action(**arguments)
                else:
                    result = f"Erro: Ferramenta {function_name} não encontrada."
            except Exception as e:
                result = f"Erro ao executar {function_name}: {str(e)}"
                logger.error(result)
            
            # Adiciona o resultado da tool à memória
            memory[channel_id].append({
                "role": "tool",
                "content": str(result)
            })

# --- CONFIGURAÇÃO SLACK BOLT ---

app = AsyncApp(token=SLACK_BOT_TOKEN)

@app.event("app_mention")
async def handle_mentions(event, say):
    user_text = event.get("text", "").replace(f"<@{SLACK_BOT_USER_ID}>", "").strip()
    channel_id = event.get("channel")
    await run_agent(channel_id, user_text)

@app.event("message")
async def handle_messages(event, say):
    # Apenas responde em DMs (canais que começam com D)
    channel_id = event.get("channel")
    if event.get("channel_type") == "im":
        user_text = event.get("text", "")
        await run_agent(channel_id, user_text)

async def main():
    # Inicializa o scheduler
    scheduler.start()
    
    # Carrega tarefas existentes
    tasks = load_scheduled_tasks()
    for task in tasks:
        add_task_to_scheduler(task)
    
    handler = AsyncSocketModeHandler(app, SLACK_APP_TOKEN)
    await handler.start_async()

if __name__ == "__main__":
    asyncio.run(main())
