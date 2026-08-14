#!/bin/bash
set -e
echo "🚀 Iniciando rebuild/deploy (Swarm)..."
cd "$(dirname "$0")/../.."

BRANCH="${DEPLOY_BRANCH:-main}"
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
    # Derivada do ref REMOTO (origin/<branch>): é o commit que o GHCR
    # buildou no push — independe da branch local/detached HEAD do servidor.
    if [ -z "${TAG:-}" ]; then
        export TAG="${BRANCH}-$(git rev-parse --short "origin/${BRANCH}")"
    fi
    echo "🔖 Publicando imagem: ghcr.io/renanclemonini/bc-sheet-processor:${TAG}"

    # Aguarda o GitHub Actions terminar de publicar, em vez de desistir na
    # primeira tentativa. Poll a cada 15s, até 5 minutos por padrão
    # (ajustável via REBUILD_MAX_TENTATIVAS / REBUILD_INTERVALO).
    MAX_TENTATIVAS="${REBUILD_MAX_TENTATIVAS:-20}"
    INTERVALO="${REBUILD_INTERVALO:-15}"
    IMAGEM_PRONTA=false
    for i in $(seq 1 "$MAX_TENTATIVAS"); do
        if docker manifest inspect "ghcr.io/renanclemonini/bc-sheet-processor:${TAG}" >/dev/null 2>&1; then
            IMAGEM_PRONTA=true
            break
        fi
        echo "⏳ Tentativa $i/$MAX_TENTATIVAS — imagem ainda não publicada (workflow em andamento)..."
        sleep "$INTERVALO"
    done

    if [ "$IMAGEM_PRONTA" != true ]; then
        echo "❌ A imagem ${TAG} não apareceu no GHCR após $((MAX_TENTATIVAS * INTERVALO))s."
        echo "   Confira o workflow em: https://github.com/renanclemonini/bc_sheet_processor_v2/actions"
        exit 1
    fi

    echo "✅ Imagem confirmada no GHCR — pré-baixando antes do deploy..."

    # Pre-pull: o download acontece FORA da janela de downtime do stop-first.
    # Sem isso, o swarm baixaria a imagem durante o swap do container.
    echo "📥 docker pull ghcr.io/renanclemonini/bc-sheet-processor:${TAG} (pode demorar)..."
    docker pull "ghcr.io/renanclemonini/bc-sheet-processor:${TAG}"
    echo "✅ Imagem disponível localmente — aplicando deploy (swap rápido)..."

    docker stack deploy -c docker-stack.yml bc_sheets_processor_swarm
else
    echo "🎨 Só templates alterados — sincronizando com /srv/bc-sheet-processor/templates (sem deploy)."
    sudo rsync -a --delete templates/ /srv/bc-sheet-processor/templates/
fi

echo "✅ Deploy concluído!!"
