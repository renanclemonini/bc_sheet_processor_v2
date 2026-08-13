#!/bin/bash
set -e

echo "🚀 Iniciando rebuild/deploy (Swarm)..."

cd "$(dirname "$0")/../.."

BRANCH="${DEPLOY_BRANCH:-docker-swarm-migration}"
ANTES=$(git rev-parse HEAD)
git pull origin "$BRANCH"
DEPOIS=$(git rev-parse HEAD)

# Sincroniza os valores não-sensíveis do .env para a interpolação do stack
# file (N8N_WEBHOOK_URL, WORKERS).
set -a
. ./.env
set +a

if [ "$ANTES" == "$DEPOIS" ]; then
    echo "ℹ️  Nada novo para atualizar."
    exit 0
fi

ARQUIVOS_ALTERADOS=$(git diff --name-only "$ANTES" "$DEPOIS")

# Se só mudou algo dentro de templates/, não precisa de imagem nova nem
# redeploy: os templates são bind mount de /srv/bc-sheet-processor/templates,
# só sincronizamos (Jinja2 recarrega sozinho).
if echo "$ARQUIVOS_ALTERADOS" | grep -qv '^templates/'; then
    echo "🔧 Código ou dependências alteradas — a imagem nova já foi publicada"
    echo "   pelo GitHub Actions no push; aplicando deploy..."

    # TAG imutável automática (mesmo padrão do workflow); override manual
    # continua válido: export TAG=main-<sha>
    if [ -z "${TAG:-}" ]; then
        TAG="$(git branch --show-current)-$(git rev-parse --short HEAD)"
    fi
    echo "🔖 Publicando imagem: ghcr.io/renanclemonini/bc-sheet-processor:${TAG}"

    # Nunca deploya referência que o workflow ainda não publicou
    if ! docker manifest inspect "ghcr.io/renanclemonini/bc-sheet-processor:${TAG}" >/dev/null 2>&1; then
        echo "⚠️  A imagem ${TAG} ainda não existe no GHCR (workflow em andamento)."
        echo "   Aguarde a action terminar e rode este script de novo."
        exit 1
    fi

    docker stack deploy -c docker-stack.yml bc_sheets_processor_swarm
else
    echo "🎨 Só templates alterados — sincronizando com /srv/bc-sheet-processor/templates (sem deploy)."
    sudo rsync -a --delete templates/ /srv/bc-sheet-processor/templates/
fi

echo "✅ Deploy concluído!!"