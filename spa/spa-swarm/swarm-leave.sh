#!/bin/bash
set -e

cd "$(dirname "$0")/../.."

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Desmontando o Docker Swarm...${NC}\n"

STATE=$(docker info --format '{{.Swarm.LocalNodeState}}')

if [ "$STATE" != "inactive" ]; then
    # Remove o stack antes de sair do swarm (se existir)
    if docker stack ls --format '{{.Name}}' | grep -qx "bc_sheets_processor_swarm"; then
        echo -e "${YELLOW}Removendo stack bc_sheets_processor_swarm...${NC}"
        docker stack rm bc_sheets_processor_swarm
    fi

    echo -e "${YELLOW}Abandonando o modo swarm do host...${NC}"
    docker swarm leave --force
    echo -e "${GREEN}✅ Modo swarm desativado.${NC}"
else
    echo -e "${GREEN}✅ Swarm já estava inativo.${NC}"
fi

echo -e "${GREEN}✅ Concluído! Host sem swarm.${NC}\n"