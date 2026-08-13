#!/bin/bash

cd "$(dirname "$0")/../.."

GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN} Mostrando logs...${NC}\n"

docker compose logs -f sheet-processor --tail=5
