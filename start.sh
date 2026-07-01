#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Iniciando setup do Docker...${NC}\n"

# Para containers anteriores se existirem
echo -e "${YELLOW}📦 Parando containers anteriores...${NC}"
docker compose down

# Sobe os containers
echo -e "${GREEN}🚀 Subindo os containers...${NC}"
docker compose up -d --build

sleep 3

echo -e "${GREEN}✅ Setup concluído! Mostrando logs...${NC}\n"
