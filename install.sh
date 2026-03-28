#!/bin/bash

# a1gente - Script de Instalação Automática
# Para Ubuntu 24.04 ARM64 (nordicclaw)

set -e

echo "🚀 Iniciando a instalação do a1gente..."

# 1. Atualização do Sistema e Dependências
echo "📦 Atualizando pacotes do sistema..."
apt update && apt install -y python3-venv python3-full curl git htop

# 2. Instalação do Ollama (se não existir)
if ! command -v ollama &> /dev/null; then
    echo "🧠 Instalando Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "✅ Ollama já está instalado."
fi

# 3. Configuração do Ambiente Python
echo "🐍 Configurando ambiente virtual Python..."
cd "$(dirname "$0")"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configuração do .env (Se não existir)
if [ ! -f .env ]; then
    echo "📝 Criando arquivo .env básico..."
    cat > .env <<EOF
SLACK_BOT_TOKEN=xoxb-seu-token
SLACK_APP_TOKEN=xapp-seu-token
SLACK_BOT_USER_ID=UXXXXXXXXXX
OLLAMA_URL=http://localhost:11434
MODEL_NAME=llama3.2:3b
EOF
    echo "⚠️  AVISO: Edite o arquivo .env com seus tokens do Slack antes de rodar o agente."
fi

# 5. Criação do Serviço Systemd para Ollama
echo "⚙️ Configurando serviço do Ollama..."
cat > /etc/systemd/system/ollama.service <<EOF
[Unit]
Description=Ollama Server
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/ollama serve
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_KEEP_ALIVE=24h"
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 6. Criação do Serviço Systemd para a1gente
echo "⚙️ Configurando serviço do a1gente..."
AGENT_PATH=$(pwd)
cat > /etc/systemd/system/a1gente.service <<EOF
[Unit]
Description=a1gente Slack Agent
After=ollama.service network.target

[Service]
Type=simple
User=root
WorkingDirectory=$AGENT_PATH
ExecStart=$AGENT_PATH/venv/bin/python $AGENT_PATH/agent.py
Restart=always
RestartSec=5
EnvironmentFile=$AGENT_PATH/.env

[Install]
WantedBy=multi-user.target
EOF

# 7. Ativação dos Serviços
echo "🔄 Ativando serviços..."
systemctl daemon-reload
systemctl enable ollama
systemctl enable a1gente
systemctl restart ollama
systemctl restart a1gente
sleep 5 # Espera serviços subirem

# 8. Pré-carregamento do Modelo
echo "📥 Baixando modelo llama3.2:3b (isso pode demorar)..."
ollama pull llama3.2:3b

echo "✅ Instalação concluída!"
echo "👉 Use 'systemctl status a1gente' para verificar o agente."
echo "👉 Use 'journalctl -u a1gente -f' para ver os logs em tempo real."
