#!/bin/bash
set -e
echo "🚀 Iniciando update de produção (deploy + interface)..."
cd "$(dirname "$0")/../.."

# 1. Deploy: pull → TAG remota → espera GHCR → pre-pull → stack deploy
./spa/spa-swarm/new-rebuild.sh

# 2. Interface: sincroniza templates para o bind mount (sempre)
sudo rsync -a --delete templates/ /srv/bc-sheet-processor/templates/
echo "🎨 templates/ sincronizados com /srv/bc-sheet-processor/templates"

# 3. Confirmação
docker stack services bc_sheets_processor_swarm

echo "✅ Update concluído!"