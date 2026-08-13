#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/../.."

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

TOTAL=5
SUCESSOS=0
TESTE_DIR="/tmp/opencode/swarm-test-local"

# --- helpers ---------------------------------------------------------------
step() {
    local n="$1"; shift
    echo ""
    echo -e "${BOLD}${BLUE}===== [${n}/${TOTAL}] Executando: ${NC}$*"
    echo -e "${BOLD}${BLUE}════════════════════════════════════════════════════${NC}"
}

run() {
    if "$@"; then
        SUCESSOS=$((SUCESSOS+1))
        echo -e "${GREEN}✅ Passo concluído: $*${NC}"
    else
        echo -e "${RED}❌ Falhou no passo: $*${NC}"
        echo -e "${YELLOW}   Nada mais foi executado. Resolva e rode o script de novo.${NC}"
        exit 1
    fi
}

criar_dados_teste() {
    mkdir -p "$TESTE_DIR"/{uploads,output}
    cp -r templates/. "$TESTE_DIR/templates/"
    cat > "$TESTE_DIR/docker-stack.localtest.yml" <<EOF
# Override gerado pelo test-local.sh — SOMENTE teste local (sem /srv/sudo).
services:
  sheet-processor:
    volumes:
      - $TESTE_DIR/uploads:/home/bcsheetprocessor/uploads
      - $TESTE_DIR/output:/home/bcsheetprocessor/output
      - $TESTE_DIR/templates:/home/bcsheetprocessor/templates
EOF
}

# --- execução --------------------------------------------------------------
echo -e "${BOLD}🧪 TESTE LOCAL — BC Sheet Processor (Docker Swarm)${NC}"
echo -e "   Ordem: abaixo, cada passo mostra o arquivo sendo executado."

# Pré-limpeza: se um teste anterior deixou o stack no ar, derruba antes de
# subir (evita a porta 8000 ocupada pelo container do swarm antigo)
if docker stack ls --format '{{.Name}}' 2>/dev/null | grep -qx "bc_sheets_processor_swarm"; then
    echo ""
    echo -e "${YELLOW}⚠️  Stack do teste anterior ainda está no ar — derrubando: ./spa/spa-swarm/service-down.sh${NC}"
    ./spa/spa-swarm/service-down.sh
    # o docker stack rm é assíncrono: espera os containers realmente saírem
    # (liberam a porta 8000 antes do preflight do service-up.sh)
    echo -e "${YELLOW}   Aguardando containers do stack serem removidos...${NC}"
    for i in $(seq 1 30); do
        docker ps -q --filter name=bc_sheets_processor_swarm | grep -q . || break
        sleep 2
    done
fi

step 1 "docker compose down (liberar a porta 8000 do container local)"
run docker compose down

step 2 "Preparar dados de teste e override em ${TESTE_DIR}"
run criar_dados_teste

step 3 "Executando: ./spa/spa-swarm/swarm-init.sh"
run ./spa/spa-swarm/swarm-init.sh

step 4 "Executando: ./spa/spa-swarm/service-up.sh (com STACK_OVERRIDE_FILE)"
run env STACK_OVERRIDE_FILE="$TESTE_DIR/docker-stack.localtest.yml" ./spa/spa-swarm/service-up.sh

step 5 "Executando: ./spa/spa-swarm/smoke-test.sh"
run ./spa/spa-swarm/smoke-test.sh

# --- resumo final ----------------------------------------------------------
echo ""
echo -e "${BOLD}${GREEN}✅ TESTE LOCAL CONCLUÍDO (${SUCESSOS}/${TOTAL} passos) — sistema NO AR${NC}"
echo -e "   Acesse: http://localhost:8000"
echo -e "   Container: docker ps (buscando por bc_sheets_processor_swarm)"
echo ""
echo -e "${BOLD}Para derrubar quando terminar:${NC}"
echo "   ./spa/spa-swarm/service-down.sh    # remove o stack (derruba o app)"
echo "   ./spa/spa-swarm/swarm-leave.sh     # opcional: desliga o modo swarm do host"
echo "   docker compose up -d               # opcional: restaura o container compose local"