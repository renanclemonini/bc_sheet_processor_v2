#!/bin/bash

NC='\033[0m' # No Color

echo -e "${GREEN} Mostrando logs...${NC}\n"

docker compose logs -f sheet-processor --tail=5
