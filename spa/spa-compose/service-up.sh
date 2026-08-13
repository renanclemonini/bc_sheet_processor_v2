#!/bin/bash

cd "$(dirname "$0")/../.."

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Iniciando setup do Docker...${NC}\n"

# Sobe os containers
echo -e "${GREEN}🚀 Subindo os containers...${NC}"
docker compose up -d

echo -e "${YELLOW}⏳ Aguardando o serviço ficar disponível...${NC}"

# Cria um link clicável no terminal
criar_link() {
    local url="$1"
    local texto="${2:-$url}"
    echo -e "\e]8;;${url}\e\\${texto}\e]8;;\e\\"
}

MAX_TENTATIVAS=10
for i in $(seq 1 $MAX_TENTATIVAS); do
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000)
    if [ "$HTTP_STATUS" -eq 200 ]; then
        echo -e "${GREEN}✅ Serviço online e respondendo corretamente (HTTP $HTTP_STATUS)${NC}"
        echo -e "${BLUE}🔗 Acesse em: $(criar_link "http://localhost:8000")${NC}\n"
        xdg-open http://localhost:8000 &>/dev/null &
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
fi
