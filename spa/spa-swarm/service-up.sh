#!/bin/bash
set -e

cd "$(dirname "$0")/../.."

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

STACK="bc_sheets_processor_swarm"
SERVICE="${STACK}_sheet-processor"
IMAGE_TAG="${TAG:-latest}"
IMAGE="ghcr.io/renanclemonini/bc-sheet-processor:${IMAGE_TAG}"

echo -e "${BLUE}🐳 Subindo o stack no Swarm...${NC}\n"

# --- Pré-flight: cada falha aponta a correção certa ---
fail() {
    echo -e "${RED}❌ $1${NC}"
    echo -e "${YELLOW}   $2${NC}"
    exit 1
}

STATE=$(docker info --format '{{.Swarm.LocalNodeState}}')
[ "$STATE" != "inactive" ] || fail "Swarm inativo no host." "Rode antes: ./spa/spa-swarm/swarm-init.sh"

NODE_ID=$(docker node ls -q | head -1)
docker node inspect "$NODE_ID" --format '{{.Spec.Labels}}' | grep -q "app:bc-sheet-processor" \
    || fail "Label app=bc-sheet-processor ausente no nó." "Rode: ./spa/spa-swarm/swarm-init.sh"

for NAME in bcsp_redis_url bcsp_n8n_webhook_user bcsp_n8n_webhook_password; do
    docker secret ls --format '{{.Name}}' | grep -qx "$NAME" \
        || fail "Secret '$NAME' não existe." "Rode: ./spa/spa-swarm/swarm-init.sh (ou crie manualmente)"
done

# Porta 8000 livre (mode: host faz bind direto — mostra quem está ocupando)
if ss -ltn 2>/dev/null | grep -q ':8000 '; then
    OCUPANTE=$(ss -ltnp 2>/dev/null | grep ':8000 ' | head -1)
    fail "Porta 8000 já está em uso (bind direto mode:host)." "Processo: $OCUPANTE — pare o que estiver escutando (ex.: docker compose down) e rode de novo."
fi

# Override deliberado de volumes (somente para teste local em máquina sem
# /srv, ex.: STACK_OVERRIDE_FILE=/tmp/docker-stack.localtest.yml).
# Em produção NÃO setar — o /srv é obrigatório.
OVERRIDE="${STACK_OVERRIDE_FILE:-}"
if [ -n "$OVERRIDE" ]; then
    echo -e "${YELLOW}⚠️  Usando override de volumes: $OVERRIDE (modo teste local)${NC}"
    DEPLOY_CMD=(docker stack deploy -c docker-stack.yml -c "$OVERRIDE" "$STACK")
else
    [ -d /srv/bc-sheet-processor ] \
        || fail "/srv/bc-sheet-processor não existe." "Rode: ./spa/spa-swarm/swarm-init.sh (ou crie com sudo + cp -r templates/. /srv/bc-sheet-processor/templates/)"
    DEPLOY_CMD=(docker stack deploy -c docker-stack.yml "$STACK")
fi

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Imagem $IMAGE não está localmente — o Swarm vai tentar puxar do GHCR.${NC}"
fi

# --- Deploy com captura de output (em if para o set -e não engolir o erro) ---
set -a
. ./.env
set +a

if ! OUTPUT=$("${DEPLOY_CMD[@]}" 2>&1); then
    echo -e "${RED}❌ Deploy falhou:${NC}"
    echo "$OUTPUT" | tail -5
    if echo "$OUTPUT" | grep -q "secret not found"; then
        echo -e "${YELLOW}   → Secret referenciado não existe. Rode: ./spa/spa-swarm/swarm-init.sh${NC}"
    elif echo "$OUTPUT" | grep -q "port is already allocated"; then
        echo -e "${YELLOW}   → Porta em uso. Veja o processo com: ss -ltnp | grep :8000${NC}"
    elif echo "$OUTPUT" | grep -q "node.labels"; then
        echo -e "${YELLOW}   → Constraint de nó não satisfeita. Rode: ./spa/spa-swarm/swarm-init.sh${NC}"
    fi
    exit 1
fi

# --- Readiness com escape (falha rápida se a task falhar) ---
MAX_TENTATIVAS=10
for i in $(seq 1 $MAX_TENTATIVAS); do
    TASK_ERR=$(docker service ps "$SERVICE" --format '{{.CurrentState}}|{{.Error}}' 2>/dev/null | grep -E 'Failed|Rejected|Error' | head -1 || true)
    if [ -n "$TASK_ERR" ]; then
        echo -e "${RED}❌ Task falhou:${NC} $TASK_ERR"
        echo -e "${YELLOW}   Logs: ./spa/spa-swarm/logs.sh${NC}"
        exit 1
    fi

    # || true: curl retorna exit != 0 enquanto a porta ainda não aceita conexão
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000 || true)
    if [ "$HTTP_STATUS" -eq 200 ]; then
        echo -e "${GREEN}✅ Serviço online e respondendo corretamente (HTTP $HTTP_STATUS)${NC}"
        break
    elif [ "$HTTP_STATUS" -eq 000 ]; then
        echo -e "${YELLOW}Tentativa $i/$MAX_TENTATIVAS... (serviço ainda não está aceitando conexões)${NC}"
    else
        echo -e "${YELLOW}Tentativa $i/$MAX_TENTATIVAS... (respondeu, mas com HTTP $HTTP_STATUS)${NC}"
    fi
    sleep 7
done

if [ "$HTTP_STATUS" -ne 200 ]; then
    echo -e "${RED}❌ Serviço não respondeu após $MAX_TENTATIVAS tentativas${NC}"
    echo -e "${YELLOW}   Logs: ./spa/spa-swarm/logs.sh${NC}"
    exit 1
fi

# --- Estado final ---
docker service ls
echo ""
docker ps --filter name="$STACK" --format '{{.Names}} | {{.Status}}'