#!/bin/bash

# a1gente - Script de Desinstalação
# CUIDADO: Isso removerá os serviços e o ambiente virtual de Python.

set -e

if [[ $EUID -ne 0 ]]; then
   echo "🚫 Este script deve ser rodado como root (sudo)."
   exit 1
fi

echo "🗑️  Iniciando a remoção do a1gente..."

# 1. Parar e Desativar Serviços
echo "⏹️  Parando serviços..."
systemctl stop a1gente || true
systemctl disable a1gente || true
systemctl stop ollama || true
systemctl disable ollama || true

# 2. Remover Arquivos de Serviço Systemd
echo "📂 Removendo arquivos de sistema..."
rm -f /etc/systemd/system/a1gente.service
rm -f /etc/systemd/system/ollama.service
systemctl daemon-reload

# 3. Remover Venv e Logs (Mantém diretório e .env por segurança)
echo "🧹 Limpando ambiente virtual e arquivos de cache..."
cd "$(dirname "$0")"
rm -rf venv/
rm -rf *.log
rm -rf __pycache__

echo "✅ Desinstalação concluída!"
echo "👉 O diretório do projeto e o seu arquivo .env foram MANTIDOS por segurança."
echo "👉 Se quiser remover o Ollama completamente, use 'ollama --version' para checar e 'apt purge ollama'."
