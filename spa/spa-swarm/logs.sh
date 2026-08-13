#!/bin/bash

cd "$(dirname "$0")/../.."

GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN} Mostrando logs (Swarm)...${NC}\n"

docker service logs -f bc_sheets_processor_swarm_sheet-processor --tail=5