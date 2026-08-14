#!/bin/bash
set -e
echo "🚀 Iniciando update de produção (deploy + interface)..."
cd "$(dirname "$0")/../.."

# Remove marcador de "deploy pulado" de uma execução anterior, se existir
rm -f .deploy-skipped

# 1. Deploy: pull → TAG remota → espera GHCR → pre-pull → stack deploy
./spa/spa-swarm/new-rebuild.sh

# 2. Interface: sincroniza templates para o bind mount (sempre), EXCETO
#    quando o new-rebuild.sh sinalizou (criou .deploy-skipped) que o pull
#    não trouxe nada deployável (só docs/testes) — não há o que sincronizar.
if [ -f .deploy-skipped ]; then
    echo "⚠ Update pulado: o pull só trouxe arquivos sem deploy (docs/testes)."
    echo "   Sem deploy de imagem; templates, se alterados, já foram sincronizados pelo new-rebuild.sh."
    rm -f .deploy-skipped
else
    sudo rsync -a --delete templates/ /srv/bc-sheet-processor/templates/
    echo "🎨 templates/ sincronizados com /srv/bc-sheet-processor/templates"
fi

# 3. Confirmação
docker stack services bc_sheets_processor_swarm

echo "✅ Update concluído!"