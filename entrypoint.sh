#!/bin/ash
set -e

# --- Leitura de Docker secrets (Swarm) ---
# Secrets do Swarm chegam como arquivo em /run/secrets/, não como env var.
# O config.py espera REDIS_URL / N8N_WEBHOOK_USER / N8N_WEBHOOK_PASSWORD /
# TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID como env var comum, então exportamos
# aqui se o arquivo existir.
# Se rodar via `docker compose up` (sem secrets), os `if` não entram e o
# .env normal (via `environment:` do compose) continua funcionando igual.
if [ -f /run/secrets/bcsp_redis_url ]; then
  export REDIS_URL="$(cat /run/secrets/bcsp_redis_url)"
fi
if [ -f /run/secrets/bcsp_n8n_webhook_user ]; then
  export N8N_WEBHOOK_USER="$(cat /run/secrets/bcsp_n8n_webhook_user)"
fi
if [ -f /run/secrets/bcsp_n8n_webhook_password ]; then
  export N8N_WEBHOOK_PASSWORD="$(cat /run/secrets/bcsp_n8n_webhook_password)"
fi
if [ -f /run/secrets/bcsp_telegram_bot_token ]; then
  export TELEGRAM_BOT_TOKEN="$(cat /run/secrets/bcsp_telegram_bot_token)"
fi
if [ -f /run/secrets/bcsp_telegram_chat_id ]; then
  export TELEGRAM_CHAT_ID="$(cat /run/secrets/bcsp_telegram_chat_id)"
fi
# --- fim do trecho ---

chown -R __USERNAME__:__USERNAME__ /home/__USERNAME__/uploads /home/__USERNAME__/output
# Diretório de logs de falha (bind mount em ${HOME}/logs no host do Swarm)
install -d -o __USERNAME__ -g __USERNAME__ /home/__USERNAME__/logs

exec su-exec __USERNAME__ poetry run python run.py