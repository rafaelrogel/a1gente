from typing import List, Dict, Any, Optional
import logging
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_slack_message",
            "description": "Lê o texto original da mensagem recebida.",
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
            "description": "Cria um post de blog em Markdown.",
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
            "description": "Busca o conteúdo textual de uma URL.",
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
            "description": "Solicita um resumo.",
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
            "description": "Envia uma resposta para o Slack.",
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
            "description": "Pesquisa na internet usando DuckDuckGo.",
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
            "description": "Agenda uma tarefa periódica (ex: todo dia às 9h).",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "O que fazer na execução.",
                    },
                    "recurrence": {
                        "type": "string",
                        "description": "Regra (ex: todo dia às 9h).",
                    },
                    "channel": {
                        "type": "string",
                        "description": "ID do canal Slack (C...).",
                    },
                },
                "required": ["prompt", "recurrence", "channel"],
            },
        },
    },
]


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
    else:
        return f"Erro: {name} não encontrada."
