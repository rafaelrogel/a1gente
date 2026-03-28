#!/bin/bash

# a1gente - Script de Atualização
# Atualiza o código, dependências e reinicia o serviço.

set -e

echo "🔄 Iniciando atualização do a1gente..."

# 1. Pull de mudanças se for um repositório git
if [ -d .git ]; then
    echo "⬇️  Buscando atualizações no Git..."
    git pull origin main || git pull origin master
else
    echo "⚠️  Não é um repositório Git, pulando busca de código."
fi

# 2. Atualizar venv
echo "📦 Atualizando dependências no ambiente virtual..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. Reiniciar serviços
echo "⚙️  Reiniciando serviço a1gente..."
systemctl daemon-reload
systemctl restart a1gente

# 4. Status
echo "✅ Atualização concluída!"
echo "👉 Status do serviço:"
systemctl status a1gente --no-pager
echo "👉 Logs recentes:"
journalctl -u a1gente -n 10 --no-pager
