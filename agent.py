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
    A1MBRA_CHANNEL,
)
from memory import update_memory, get_memory, clear_memory
from ollama_client import call_ollama
from tools import TOOLS, execute_tool
from scheduler import (
    scheduler,
    load_scheduled_tasks,
    add_task_to_scheduler,
    add_job_scout_task,
    is_job_scout_active,
)
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = AsyncApp(token=SLACK_BOT_TOKEN)


async def run_agent(channel_id: str, user_text: str, user_id: str = None):
    instructions = (
        "Você é o Nordic-Claw, assistente Slack inteligente e proativo. REGRAS CRÍTICAS:\n"
        "1. Use tools diretamente via 'tool_calls' quando necessário. NUNCA mostre JSON no chat.\n"
        f"2. Se for agendar para este canal, o ID é '{channel_id}'.\n"
        "3. Responda SEMPRE em Português Brasileiro (pt-BR). Nunca responda em English ou outro idioma.\n"
        "4. NUNCA invente informações, links, resultados de comandos, código ou notícias. Se não tiver certeza, diga que não sabe.\n"
        "5. Ao usar web_search, apresenta APENAS os resultados reais retornados pela ferramenta. Não adiciona nem altere informações.\n"
        "6. Links devem ser copiados exatamente como retornados pela ferramenta de busca.\n"
        "7. SE o usuário pedir para executar comandos do sistema (como 'ls', 'df', 'uptime', 'git status', 'ps', etc), você DEVE usar a ferramenta 'run_sysadmin_command' com o comando exato. NUNCA invente a saída de um comando.\n"
        "8. Para ver o status do sistema (CPU, RAM, disco), use a ferramenta 'get_system_status'.\n"
        "9. Para verificar status de serviços, use 'get_service_status'.\n"
        "10. Para ver logs, use 'get_recent_logs'.\n"
        "11. Para ver status do git, use 'get_git_status'.\n"
        "12. SE o usuário pedir para executar codigo Python, você DEVE usar a ferramenta 'execute_python_code'. NUNCA finja que executou codigo.\n"
        "13. NUNCA finja que executou um comando ou codigo. SEMPRE use as ferramentas disponíveis.\n"
        "14. Para memória de longo prazo, armazene fatos importantes e preferências do usuário quando solicitado.\n"
        "15. SEJA INTELIGENTE E PROATIVO: Quando uma busca falhar, tente alternativas. Quando o usuário mencionar algo vagamente, tente entender a intenção e use a melhor ferramenta.\n"
        "16. Quando searches falharem (reddit, vagas, etc), tente variações, sinônimos, ou busca geral primeiro.\n"
        "17. Antecipe necessidades: se o usuário pedir algo complexo, sugira próximos passos lógicos.\n"
        "18. Se uma ferramenta retornar erro ou 'nenhum resultado', NÃO PARE - tente outra abordagem.\n"
    )

    if not get_memory(channel_id):
        update_memory(channel_id, "system", instructions, max_memory=MAX_MEMORY)

    if user_id:
        try:
            from long_term_memory import get_memory_context_for_user

            ltm_context = get_memory_context_for_user(user_id)
            if ltm_context:
                update_memory(
                    channel_id,
                    "system",
                    f"Contexto de memória de longo prazo para o usuário:\n{ltm_context}",
                    max_memory=MAX_MEMORY,
                )
        except Exception as e:
            logger.warning(f"Erro ao carregar memória de longo prazo: {e}")

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
                await app.client.chat_postMessage(channel=channel_id, text=content)
            break

        for tc in tool_calls:
            fn = tc["function"]["name"]
            args = tc["function"]["arguments"]
            logger.info(f"Ferramenta: {fn}")

            res = ""
            try:
                res = await execute_tool(fn, args, app=app)
            except Exception as e:
                res = f"Erro {fn}: {str(e)}"

            update_memory(channel_id, "tool", str(res), max_memory=MAX_MEMORY)


async def run_scheduled_task(task: Dict[str, Any]):
    from datetime import datetime

    logger.info(f"Executando tarefa agendada: {task['prompt']}")

    now = datetime.now()
    date_prefix = now.strftime("%d/%m/%Y às %H:%M")

    clear_memory(task["channel"])

    await run_agent(task["channel"], f"[{date_prefix}] {task['prompt']}")


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
        await app.client.chat_postMessage(channel=channel, text=msg)
        return f"Tarefa agendada e confirmada: {msg}"
    except Exception as e:
        logger.error(f"Erro ao agendar tarefa: {e}")
        return f"Erro ao agendar tarefa: {str(e)}"


@app.event("app_mention")
async def handle_mentions(event, say):
    text = event.get("text", "").replace(f"<@{SLACK_BOT_USER_ID}>", "").strip()
    if text:
        user_id = event.get("user")
        await run_agent(event.get("channel"), text, user_id=user_id)


@app.event("message")
async def handle_messages(event, say):
    if event.get("channel_type") == "im":
        if event.get("bot_id"):
            return
        text = event.get("text", "")
        files = event.get("files", [])

        if files:
            await app.client.chat_postMessage(
                channel=event.get("channel"),
                text="Desculpe, este modelo de IA não suporta entrada de imagens. Posso ajudar com texto, comandos do sistema, execução de código Python, geração de imagens, clima, tradução, notas, lembretes e muito mais!",
            )
            return

        if text:
            user_id = event.get("user")
            await run_agent(event.get("channel"), text, user_id=user_id)


async def main():
    scheduler.start()
    for t in load_scheduled_tasks():
        add_task_to_scheduler(t, run_scheduled_task)
    from reminders import init_scheduler

    init_scheduler()
    handler = AsyncSocketModeHandler(app, SLACK_APP_TOKEN)
    await handler.start_async()


if __name__ == "__main__":
    asyncio.run(main())
