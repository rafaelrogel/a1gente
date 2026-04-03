import asyncio
import json
import re
import logging
from typing import List, Dict, Any

from config import (
    SLACK_BOT_TOKEN,
    SLACK_APP_TOKEN,
    SLACK_BOT_USER_ID,
    MAX_MEMORY,
    MAX_ITERATIONS,
)
from memory import update_memory, get_memory
from ollama_client import call_ollama
from tools import TOOLS, execute_tool
from scheduler import scheduler, load_scheduled_tasks, add_task_to_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = None


def get_app():
    global app
    if app is None:
        from slack_bolt.async_app import AsyncApp
        from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

        app = AsyncApp(token=SLACK_BOT_TOKEN)
    return app


async def run_agent(channel_id: str, user_text: str):
    instructions = (
        "Você é o Nordic-Claw, assistente Slack. REGRAS CRÍTICAS:\n"
        "1. Use tools diretamente via 'tool_calls' quando necessário. NÃO mostre JSON no chat.\n"
        f"2. Se for agendar para este canal, o ID é '{channel_id}'.\n"
        "3. Responda sempre em Português.\n"
        "4. NUNCA invente informações, links ou notícias. Se não tiver certeza, diga que não sabe.\n"
        "5. Ao usar web_search, apresenta APENAS os resultados reais retornados pela ferramenta. Não adicione nem altere informações.\n"
        "6. Links devem ser copiados exatamente como retornados pela ferramenta de busca."
    )

    if not get_memory(channel_id):
        update_memory(channel_id, "system", instructions, max_memory=MAX_MEMORY)

    update_memory(channel_id, "user", user_text, max_memory=MAX_MEMORY)

    for i in range(MAX_ITERATIONS):
        logger.info(f"Iteração {i + 1} - Canal: {channel_id}")
        response_data = await call_ollama(get_memory(channel_id), tools=TOOLS)
        message = response_data.get("message", {})
        content = message.get("content", "")
        tool_calls = message.get("tool_calls", [])

        if not tool_calls and "{" in content and "}" in content:
            try:
                j_match = re.search(r"\{.*\}", content, re.DOTALL)
                if j_match:
                    manual = json.loads(j_match.group(0))
                    if "name" in manual:
                        tool_calls = [
                            {
                                "function": {
                                    "name": manual["name"],
                                    "arguments": manual.get(
                                        "parameters", manual.get("arguments", {})
                                    ),
                                }
                            }
                        ]
                        content = content.replace(j_match.group(0), "").strip()
            except json.JSONDecodeError as e:
                logger.warning(f"Fallback JSON parse failed: {e}")
            except Exception as e:
                logger.error(f"Unexpected error in fallback JSON parsing: {e}")

        update_memory(
            channel_id,
            "assistant",
            content,
            tool_calls=tool_calls,
            max_memory=MAX_MEMORY,
        )

        if not tool_calls:
            if content:
                await get_app().client.chat_postMessage(
                    channel=channel_id, text=content
                )
            break

        for tc in tool_calls:
            fn = tc["function"]["name"]
            args = tc["function"]["arguments"]
            logger.info(f"Ferramenta: {fn}")

            res = ""
            try:
                res = await execute_tool(fn, args)
            except Exception as e:
                res = f"Erro {fn}: {str(e)}"

            update_memory(channel_id, "tool", str(res), max_memory=MAX_MEMORY)


async def run_scheduled_task(task: Dict[str, Any]):
    logger.info(f"Executando tarefa agendada: {task['prompt']}")
    await run_agent(task["channel"], f"TAREFA AGENDADA: {task['prompt']}")


async def schedule_action(prompt: str, recurrence: str, channel: str) -> str:
    """Agenda uma ação recorrente."""
    from datetime import datetime
    from scheduler import save_scheduled_tasks, add_task_to_scheduler

    try:
        tasks = load_scheduled_tasks()
        new_task = {
            "id": f"task_{int(datetime.now().timestamp())}",
            "prompt": prompt,
            "recurrence": recurrence,
            "channel": channel,
            "created_at": datetime.now().isoformat(),
        }
        tasks.append(new_task)
        save_scheduled_tasks(tasks)
        add_task_to_scheduler(new_task, run_scheduled_task)

        msg = f"✅ *Agendado com sucesso!*\n\n• *Ação*: {prompt}\n• *Frequência*: {recurrence}\n• *Canal*: <#{channel}>"
        await get_app().client.chat_postMessage(channel=channel, text=msg)
        return f"Tarefa agendada e confirmada: {msg}"
    except Exception as e:
        logger.error(f"Erro ao agendar tarefa: {e}")
        return f"Erro ao agendar tarefa: {str(e)}"


@app.event("app_mention")
async def handle_mentions(event, say):
    text = event.get("text", "").replace(f"<@{SLACK_BOT_USER_ID}>", "").strip()
    if text:
        await run_agent(event.get("channel"), text)


@app.event("message")
async def handle_messages(event, say):
    if event.get("channel_type") == "im":
        if event.get("bot_id"):
            return
        text = event.get("text", "")
        if text:
            await run_agent(event.get("channel"), text)


async def main():
    scheduler.start()
    for t in load_scheduled_tasks():
        add_task_to_scheduler(t, run_scheduled_task)
    handler = AsyncSocketModeHandler(get_app(), SLACK_APP_TOKEN)
    await handler.start_async()


if __name__ == "__main__":
    asyncio.run(main())
