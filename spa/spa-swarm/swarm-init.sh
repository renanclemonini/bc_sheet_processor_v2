#!/bin/bash
set -e

cd "$(dirname "$0")/../.."

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Preparando o host para Docker Swarm...${NC}\n"

# --- 1. Modo swarm ---
STATE=$(docker info --format '{{.Swarm.LocalNodeState}}')

if [ "$STATE" == "inactive" ]; then
    echo -e "${YELLOW}Swarm inativo — inicializando...${NC}"
    # SWARM_ADVERTISE_ADDR opcional: usado na VM de produção (ex.: 10.10.10.2)
    docker swarm init ${SWARM_ADVERTISE_ADDR:+--advertise-addr $SWARM_ADVERTISE_ADDR}
    echo -e "${GREEN}✅ Swarm inicializado.${NC}"
else
    echo -e "${GREEN}✅ Swarm já está ativo ($STATE) — nada a fazer.${NC}"
fi

# --- 2. Label do nó (constraint do stack) ---
LABEL="app=bc-sheet-processor"
NODE_ID=$(docker node ls -q | head -1)

if docker node inspect "$NODE_ID" --format '{{.Spec.Labels}}' | grep -q "app:bc-sheet-processor"; then
    echo -e "${GREEN}✅ Label $LABEL já aplicado no nó.${NC}"
else
    docker node update --label-add "$LABEL" "$NODE_ID"
    echo -e "${GREEN}✅ Label $LABEL aplicado no nó ($NODE_ID).${NC}"
fi

# --- 3. Diretórios de dados (/srv) ---
if [ -d /srv/bc-sheet-processor/templates ]; then
    echo -e "${GREEN}✅ /srv/bc-sheet-processor já existe.${NC}"
else
    echo -e "${YELLOW}Criando /srv/bc-sheet-processor (sudo)...${NC}"
    if sudo -p "Senha do sudo: " sh -c 'mkdir -p /srv/bc-sheet-processor/{uploads,output,templates} && chown -R 1000:1000 /srv/bc-sheet-processor'; then
        cp -r templates/. /srv/bc-sheet-processor/templates/
        echo -e "${GREEN}✅ /srv/bc-sheet-processor criado e templates copiados.${NC}"
    else
        echo -e "${YELLOW}⚠️  Não foi possível criar /srv (sudo indisponível). Crie manualmente:${NC}"
        echo "   sudo mkdir -p /srv/bc-sheet-processor/{uploads,output,templates}"
        echo "   sudo chown -R 1000:1000 /srv/bc-sheet-processor"
        echo "   cp -r templates/. /srv/bc-sheet-processor/templates/"
    fi
fi

# --- 4. Secrets (somente leitura do .env — NUNCA edita o arquivo) ---
set -a
. ./.env
set +a

# nomes dos secrets | variável de origem no .env
declare -A SECRETS=( [bcsp_redis_url]="REDIS_URL" [bcsp_n8n_webhook_user]="N8N_WEBHOOK_USER" [bcsp_n8n_webhook_password]="N8N_WEBHOOK_PASSWORD" )

for NAME in "${!SECRETS[@]}"; do
    ENV_VAR="${SECRETS[$NAME]}"
    if docker secret ls --format '{{.Name}}' | grep -qx "$NAME"; then
        echo -e "${GREEN}✅ Secret $NAME já existe.${NC}"
    else
        VAL="${!ENV_VAR}"
        if [ -n "$VAL" ]; then
            # Valor via variável — nunca aparece na linha de comando (history/ps)
            echo -n "$VAL" | docker secret create "$NAME" -
            echo -e "${GREEN}✅ Secret $NAME criado a partir de \$$ENV_VAR do .env.${NC}"
        else
            echo -e "${YELLOW}⚠️  Secret $NAME não existe e \$$ENV_VAR está vazio no .env. Crie com:${NC}"
            echo "   echo -n '<valor>' | docker secret create $NAME -"
        fi
    fi
done

# --- Aviso de segurança (ação é sempre manual, nunca automática) ---
echo ""
echo -e "${YELLOW}🔒 Aviso: as credenciais ainda estão em texto puro no .env deste host.${NC}"
echo -e "${YELLOW}   Este script NUNCA edita o .env — se quiser removê-las, faça manualmente${NC}"
echo -e "${YELLOW}   (REDIS_URL, N8N_WEBHOOK_USER, N8N_WEBHOOK_PASSWORD) após validar o deploy.${NC}"

echo ""
echo -e "${GREEN}Pronto! Suba o app com: ./spa/spa-swarm/service-up.sh${NC}"