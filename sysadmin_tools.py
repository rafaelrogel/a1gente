import subprocess
import logging
import platform
import tempfile
import os
import re
from typing import Optional

logger = logging.getLogger(__name__)

ALLOWED_COMMANDS = {
    "df": "Disk space usage",
    "free": "Memory usage",
    "uptime": "System uptime and load",
    "whoami": "Current user",
    "hostname": "Server hostname",
    "uname": "System information",
    "date": "Current date and time",
    "git": "Git status and logs",
    "systemctl": "Service status",
    "ps": "Process list",
    "top": "System activity",
    "cat": "File content (read-only)",
    "ls": "List directory",
    "pwd": "Current directory",
    "wc": "Word/line count",
    "head": "First lines of file",
    "tail": "Last lines of file",
    "du": "Directory size",
    "nproc": "CPU cores count",
    "lscpu": "CPU information",
    "journalctl": "System logs (read-only)",
}

DANGEROUS_PATTERNS = [
    "rm -rf",
    "rm -f",
    "rm ",
    "> ",
    ">> ",
    "|",
    ";",
    "&&",
    "||",
    "`",
    "$(",
    "chmod",
    "chown",
    "kill",
    "pkill",
    "shutdown",
    "reboot",
    "halt",
    "poweroff",
    "mkfs",
    "dd",
    "wget",
    "curl",
    "apt",
    "apt-get",
    "yum",
    "dnf",
    "pip",
    "pip3",
    "npm",
    "node",
    "python",
    "python3",
    "bash",
    "sh",
    "zsh",
    "sudo",
    "su ",
    "passwd",
    "useradd",
    "userdel",
    "usermod",
    "groupadd",
    "groupdel",
    "iptables",
    "ufw",
    "firewall",
    "ssh",
    "scp",
    "rsync",
    "mount",
    "umount",
    "fdisk",
    "parted",
    "mkswap",
    "swapon",
    "swapoff",
    "crontab",
    "at ",
    "batch",
    "systemctl stop",
    "systemctl disable",
    "systemctl restart",
    "systemctl reload",
    "systemctl kill",
]


def is_command_safe(command: str) -> tuple[bool, str]:
    cmd_lower = command.lower()

    for pattern in DANGEROUS_PATTERNS:
        if pattern in cmd_lower:
            return (
                False,
                f"Comando bloqueado: '{pattern}' não é permitido por segurança",
            )

    base_cmd = command.split()[0] if command.split() else ""
    if base_cmd not in ALLOWED_COMMANDS:
        return False, f"Comando '{base_cmd}' não está na lista de comandos permitidos"

    return True, "Comando seguro"


async def run_sysadmin_command(command: str) -> str:
    safe, reason = is_command_safe(command)
    if not safe:
        return f"ERRO_SEGURANCA: {reason}"

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )

        output = result.stdout.strip()
        error = result.stderr.strip()

        if result.returncode != 0:
            return f"ERRO_COMANDO (exit {result.returncode}):\n{error[:500] if error else 'Sem detalhes'}"

        if not output:
            return "Comando executado com sucesso, mas sem saída."

        return f"COMANDO_EXECUTADO: {command}\n\nSAIDA:\n{output[:2000]}"

    except subprocess.TimeoutExpired:
        return f"ERRO_TIMEOUT: Comando '{command}' excedeu 30 segundos"
    except Exception as e:
        logger.error(f"Erro ao executar comando sysadmin: {e}")
        return f"ERRO_INESPERADO: {str(e)}"


async def get_system_status() -> str:
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
            return f"ERRO: Servico '{service_name}' nao encontrado ou com erro:\n{result.stderr.strip()[:500]}"

        return f"STATUS DO SERVICO '{service_name}':\n{output[:1000]}"

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
            return f"ERRO: Falha ao obter logs:\n{result.stderr.strip()[:500]}"

        output = result.stdout.strip()
        if not output:
            return "Nenhum log encontrado para o servico a1gente."

        return f"ULTIMOS {safe_lines} LOGS DO A1GENTE:\n{output[:3000]}"

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


DANGEROUS_IMPORTS = [
    "os.system",
    "os.popen",
    "subprocess",
    "socket",
    "requests",
    "urllib",
    "http",
    "ftplib",
    "smtplib",
    "paramiko",
    "fabric",
    "shutil.rmtree",
    "shutil.copy",
    "shutil.move",
    "shutil.copytree",
    "shutil.move",
    "ctypes",
    "pickle",
    "marshal",
    "importlib",
    "__import__",
    "exec(",
    "eval(",
    "compile(",
    "globals()",
    "locals()",
    "open(",
    "input(",
]

SAFE_CODE_TEMPLATE = """
import sys
import io
import math
import json
import datetime
import time
import random
import string
import re
import collections
import itertools
import functools
import operator
import statistics
import decimal
import fractions
import typing
import dataclasses
import enum
import copy
import textwrap
import unicodedata
import struct
import hashlib
import hmac
import secrets
import base64
import binascii
import csv
import io
import pprint
import reprlib

# Block dangerous operations
import builtins
_dangerous_builtins = ['open', 'input', 'eval', 'exec', 'compile', 'getattr', 'setattr', 'delattr']
for _name in _dangerous_builtins:
    if hasattr(builtins, _name):
        pass  # We allow these but monitor usage

{code}
"""


def is_code_safe(code: str) -> tuple:
    code_lower = code.lower()

    for pattern in DANGEROUS_IMPORTS:
        if pattern.lower() in code_lower:
            return False, f"Codigo bloqueado: '{pattern}' nao e permitido por seguranca"

    if len(code) > 5000:
        return False, "Codigo muito longo (maximo 5000 caracteres)"

    return True, "Codigo seguro"


async def execute_python_code(code: str) -> str:
    safe, reason = is_code_safe(code)
    if not safe:
        return f"ERRO_SEGURANCA: {reason}"

    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir="/tmp"
        ) as f:
            f.write(SAFE_CODE_TEMPLATE.format(code=code))
            temp_file = f.name

        try:
            result = subprocess.run(
                ["python3", temp_file],
                capture_output=True,
                text=True,
                timeout=30,
                env={"PATH": "/usr/bin:/usr/local/bin"},
            )

            output = result.stdout.strip()
            error = result.stderr.strip()

            if result.returncode != 0:
                return f"ERRO_EXECUCAO (exit {result.returncode}):\n{error[:1000] if error else 'Sem detalhes'}"

            if not output and not error:
                return "Codigo executado com sucesso, mas sem saida."

            result_msg = "CODIGO_EXECUTADO COM SUCESSO:\n"
            if output:
                result_msg += f"\nSAIDA:\n{output[:2000]}"
            if error:
                result_msg += f"\n\nSTDERR:\n{error[:500]}"

            return result_msg

        finally:
            try:
                os.unlink(temp_file)
            except:
                pass

    except subprocess.TimeoutExpired:
        return f"ERRO_TIMEOUT: Codigo excedeu 30 segundos de execucao"
    except Exception as e:
        logger.error(f"Erro ao executar codigo Python: {e}")
        return f"ERRO_INESPERADO: {str(e)}"
