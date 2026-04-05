#!/bin/bash
# Health check para o agent - mata processos Ollama travados

LOG_FILE="/var/log/agent_health.log"
MAX_RAM_PERCENT=70

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" >> $LOG_FILE
}

check_ram() {
    RAM_USED=$(free | grep Mem | awk '{print int($3*100/$2)}')
    if [ $RAM_USED -gt $MAX_RAM_PERCENT ]; then
        log "ALERTA: RAM em $RAM_USED%"
        
        # Mata processos Ollama runner travados
        pkill -f "ollama runner" && log "Matou processos ollama runner"
        
        # Reinicia o agent
        systemctl restart a1gente && log "Reiniciou agent"
    else
        log "RAM OK: $RAM_USED%"
    fi
}

check_ollama_stuck() {
    # Se há mais de 1 processo runner, mata todos
    RUNNER_COUNT=$(ps aux | grep "ollama runner" | grep -v grep | wc -l)
    if [ $RUNNER_COUNT -gt 1 ]; then
        log "ALERTA: $RUNNER_COUNT processos ollama runner"
        pkill -f "ollama runner" && log "Matou processos travados"
    fi
}

check_ram
check_ollama_stuck
