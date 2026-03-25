import os
import json
import asyncio
import httpx
import logging
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from dotenv import load_dotenv

# Configurações de Log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# --- CONFIGURAÇÕES DO USUÁRIO ---
# TODO: Coloque seu SLACK_BOT_TOKEN e SLACK_APP_TOKEN no arquivo .env ou como variáveis de ambiente
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "xoxb-seu-token-aqui")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN", "xapp-seu-token-aqui")
# TODO: Coloque o ID do usuário do bot (ex: U0123456789)
SLACK_BOT_USER_ID = os.environ.get("SLACK_BOT_USER_ID", "UXXXXXXXXXX")
# TODO: URL do Ollama (ajuste se necessário)
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
# TODO: Modelo Ollama (phi3, qwen2.5:3b ou llama3.2:3b)
MODEL_NAME = os.environ.get("MODEL_NAME", "llama3.2:3b")

# --- MEMÓRIA SIMPLES ---
# Dicionário para armazenar o histórico de mensagens por canal/usuário
# Formato: { "channel_id": [ {"role": "user/assistant", "content": "..."} ] }
memory: Dict[str, List[Dict[str, str]]] = {}
MAX_MEMORY = 10

def update_memory(channel_id: str, role: str, content: str):
    if channel_id not in memory:
        memory[channel_id] = []
    memory[channel_id].append({"role": role, "content": content})
    if len(memory[channel_id]) > MAX_MEMORY:
        # Mantém a primeira mensagem (System) se houver, e as últimas N-1
        memory[channel_id] = memory[channel_id][-MAX_MEMORY:]

# --- FERRAMENTAS (TOOLS) ---

async def read_slack_message(text: str) -> str:
    """Lê o texto da mensagem do Slack e devolve para o LLM."""
    return f"Mensagem lida: {text}"

async def write_blog_post(title: str, content: str) -> str:
    """Gera um post de blog em markdown, com estrutura de seções, subtítulos, etc."""
    blog_md = f"# {title}\n\n{content}\n\n---\n*Post gerado automaticamente pelo Agente AI*"
    # Aqui poderíamos salvar num arquivo, mas vamos retornar o texto
    return f"Blog post gerado:\n\n{blog_md}"

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
        await app.client.chat_postMessage(channel=channel, text=message)
        return "Mensagem enviada com sucesso ao Slack."
    except Exception as e:
        return f"Erro ao enviar mensagem ao Slack: {str(e)}"

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
    }
]

# --- INTEGRAÇÃO OLLAMA ---

async def call_ollama(messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    url = f"{OLLAMA_URL}/api/chat"
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False
    }
    if tools:
        payload["tools"] = tools

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=60.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao chamar Ollama: {e}")
            return {"message": {"role": "assistant", "content": f"Erro na API do Ollama: {str(e)}"}}

# --- LÓGICA DO AGENTE ---

async def run_agent(channel_id: str, user_text: str):
    # Inicializa ou recupera memória
    if channel_id not in memory:
        memory[channel_id] = [{"role": "system", "content": "Você é um assistente prestativo integrado ao Slack. Use as ferramentas disponíveis quando necessário."}]
    
    update_memory(channel_id, "user", user_text)
    
    # Loop de raciocínio (pensamento + tool use)
    for _ in range(5): # Limite de 5 iterações para evitar loops infinitos
        response_data = await call_ollama(memory[channel_id], tools=TOOLS)
        message = response_data.get("message", {})
        
        # Adiciona resposta do assistente à memória
        memory[channel_id].append(message)
        
        tool_calls = message.get("tool_calls")
        if not tool_calls:
            # Se não houver chamadas de ferramenta, para o loop e envia a resposta final se houver conteúdo
            if message.get("content"):
                await app.client.chat_postMessage(channel=channel_id, text=message["content"])
            break
        
        # Executa as ferramentas solicitadas
        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]
            
            logger.info(f"Chamando tool: {function_name} com {arguments}")
            
            result = ""
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
            
            # Adiciona o resultado da tool à memória (o Ollama espera o papel 'tool' ou 'assistant' dependendo da versão, 
            # na API de chat atual do Ollama enviamos uma mensagem com role 'tool')
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
    handler = AsyncSocketModeHandler(app, SLACK_APP_TOKEN)
    await handler.start_async()

if __name__ == "__main__":
    asyncio.run(main())
