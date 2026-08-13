#!/bin/bash

cd "$(dirname "$0")/../.."

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Remove o stack (e para containers anteriores se existirem)
echo -e "${YELLOW}📦 Removendo stack do BC Sheet Processor...${NC}"
docker stack rm bc_sheets_processor_swarm

echo -e "${GREEN}✅ Concluído! Serviço off...${NC}\n"