#!/bin/bash
set -e

echo "🚀 Iniciando deploy (Swarm)..."

cd "$(dirname "$0")/../.."

BRANCH="${DEPLOY_BRANCH:-docker-swarm-migration}"
git pull origin "$BRANCH"

# Sincroniza os valores não-sensíveis do .env para a interpolação do stack
# file (N8N_WEBHOOK_URL, WORKERS). As credenciais (REDIS_URL,
# N8N_WEBHOOK_USER/PASSWORD) já vêm dos Docker secrets.
set -a
. ./.env
set +a

# TAG imutável automática: mesmo padrão do workflow (branch-<sha>).
# Override manual continua válido: export TAG=main-<sha>
if [ -z "${TAG:-}" ]; then
    TAG="$(git branch --show-current)-$(git rev-parse --short HEAD)"
fi
echo "🔖 Publicando imagem: ghcr.io/renanclemonini/bc-sheet-processor:${TAG}"

# Confirma que o GitHub Actions já publicou essa tag no GHCR — nunca
# deploya uma referência inexistente.
if ! docker manifest inspect "ghcr.io/renanclemonini/bc-sheet-processor:${TAG}" >/dev/null 2>&1; then
    echo "⚠️  A imagem ${TAG} ainda não existe no GHCR."
    echo "   O workflow publica automaticamente no push (aguarde alguns minutos) ou,"
    echo "   se ainda não houve push, faça o commit+push para gerar a imagem."
    echo "   (Se quiser deployar a última publicada mesmo assim: export TAG=latest)"
    exit 1
fi

docker stack deploy -c docker-stack.yml bc_sheets_processor_swarm

docker stack services bc_sheets_processor_swarm

echo "✅ Deploy concluído!!"