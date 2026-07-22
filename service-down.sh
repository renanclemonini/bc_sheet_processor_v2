#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color


# Para containers anteriores se existirem
echo -e "${YELLOW}📦 Parando containers do BC Sheet Processor...${NC}"
docker compose down

echo -e "${GREEN}✅ Concluído! Serviço off...${NC}\n"
