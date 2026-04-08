import subprocess
import logging
import platform
import tempfile
import os
import re
from typing import Optional

logger = logging.getLogger(__name__)

MAX_OUTPUT_SIZE = 5000


async def run_sysadmin_command(command: str) -> str:
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
        )

        output = result.stdout.strip()
        error = result.stderr.strip()

        if result.returncode != 0:
            return f"ERRO_COMANDO (exit {result.returncode}):\n{error[:MAX_OUTPUT_SIZE] if error else 'Sem detalhes'}"

        if not output:
            return "Comando executado com sucesso, mas sem saída."

        return f"COMANDO_EXECUTADO: {command}\n\nSAIDA:\n{output[:MAX_OUTPUT_SIZE]}"

    except subprocess.TimeoutExpired:
        return f"ERRO_TIMEOUT: Comando '{command}' excedeu 60 segundos"
    except Exception as e:
        logger.error(f"Erro ao executar comando sysadmin: {e}")
        return f"ERRO_INESPERADO: {str(e)}"


async def get_system_status() -> str:
    try:
        import psutil
    except ImportError:
        pass

    try:
        commands = {
            "hostname": "hostname",
            "uptime": "uptime",
            "cpu_cores": "nproc",
            "memory": "free -h",
            "disk": "df -h /",
            "load": "cat /proc/loadavg",
        }

        results = {}
        for name, cmd in commands.items():
            try:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, timeout=10
                )
                results[name] = result.stdout.strip()
            except Exception as e:
                results[name] = f"Erro: {str(e)}"

        status = "STATUS DO SISTEMA:\n"
        status += f"Hostname: {results['hostname']}\n"
        status += f"Uptime: {results['uptime']}\n"
        status += f"CPU Cores: {results['cpu_cores']}\n"
        status += f"Memoria:\n{results['memory']}\n"
        status += f"Disco:\n{results['disk']}\n"
        status += f"Carga: {results['load']}\n"

        return status

    except Exception as e:
        logger.error(f"Erro ao obter status do sistema: {e}")
        return f"ERRO: Falha ao obter status do sistema: {str(e)}"


async def get_service_status(service_name: str) -> str:
    safe_service = "".join(c for c in service_name if c.isalnum() or c in "-_.")

    try:
        result = subprocess.run(
            f"systemctl status {safe_service}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = result.stdout.strip()

        if result.returncode != 0:
            return f"ERRO: Servico '{service_name}' nao encontrado ou com erro:\n{result.stderr.strip()[:MAX_OUTPUT_SIZE]}"

        return f"STATUS DO SERVICO '{service_name}':\n{output[:MAX_OUTPUT_SIZE]}"

    except FileNotFoundError:
        return "⚠️ systemctl não disponível neste sistema."
    except subprocess.TimeoutExpired:
        return f"ERRO_TIMEOUT: Status do servico '{service_name}' excedeu 10 segundos"
    except Exception as e:
        logger.error(f"Erro ao obter status do servico: {e}")
        return f"ERRO: Falha ao obter status do servico: {str(e)}"


async def get_recent_logs(lines: int = 20) -> str:
    try:
        safe_lines = min(max(int(lines), 5), 100)

        result = subprocess.run(
            f"journalctl -u a1gente.service -n {safe_lines} --no-pager",
            shell=True,
            capture_output=True,
            text=True,
            timeout=15,
        )

        if result.returncode != 0:
            return (
                f"ERRO: Falha ao obter logs:\n{result.stderr.strip()[:MAX_OUTPUT_SIZE]}"
            )

        output = result.stdout.strip()
        if not output:
            return "Nenhum log encontrado para o servico a1gente."

        return f"ULTIMOS {safe_lines} LOGS DO A1GENTE:\n{output[:MAX_OUTPUT_SIZE]}"

    except FileNotFoundError:
        return "⚠️ journalctl não disponível neste sistema."
    except subprocess.TimeoutExpired:
        return f"ERRO_TIMEOUT: Obtencao de logs excedeu 15 segundos"
    except Exception as e:
        logger.error(f"Erro ao obter logs: {e}")
        return f"ERRO: Falha ao obter logs: {str(e)}"


async def get_git_status() -> str:
    try:
        commands = {
            "status": "git status",
            "log": "git log --oneline -5",
            "branch": "git branch --show-current",
        }

        results = {}
        for name, cmd in commands.items():
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd="/root/a1gente",
                )
                results[name] = result.stdout.strip()
            except Exception as e:
                results[name] = f"Erro: {str(e)}"

        status = "STATUS DO GIT:\n"
        status += f"Branch: {results['branch']}\n"
        status += f"Status:\n{results['status']}\n"
        status += f"Ultimos commits:\n{results['log']}\n"

        return status

    except Exception as e:
        logger.error(f"Erro ao obter status do git: {e}")
        return f"ERRO: Falha ao obter status do git: {str(e)}"


async def execute_python_code(code: str) -> str:
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir="/tmp"
        ) as f:
            f.write(code)
            temp_file = f.name

        try:
            result = subprocess.run(
                ["python3", temp_file],
                capture_output=True,
                text=True,
                timeout=60,
            )

            output = result.stdout.strip()
            error = result.stderr.strip()

            if result.returncode != 0:
                return f"ERRO_EXECUCAO (exit {result.returncode}):\n{error[:2000] if error else 'Sem detalhes'}"

            if not output and not error:
                return "Codigo executado com sucesso, mas sem saida."

            result_msg = "CODIGO_EXECUTADO COM SUCESSO:\n"
            if output:
                result_msg += f"\nSAIDA:\n{output[:3000]}"
            if error:
                result_msg += f"\n\nSTDERR:\n{error[:1000]}"

            return result_msg

        finally:
            try:
                os.unlink(temp_file)
            except:
                pass

    except subprocess.TimeoutExpired:
        return f"ERRO_TIMEOUT: Codigo excedeu 60 segundos de execucao"
    except Exception as e:
        logger.error(f"Erro ao executar codigo Python: {e}")
        return f"ERRO_INESPERADO: {str(e)}"
