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

# Se algo NOVO chegou no pull, decide se há algo deployável. Caminhos que
# NUNCA exigem imagem nova (espelho EXATO do paths-ignore do workflow GHCR
# em .github/workflows/docker-publish.yml + templates/, que vive no bind
# mount e é sincronizado por rsync):
#   templates/, README.md, tests/, .playwright-mcp/, context-project/
SEM_DEPLOY='^templates/\|^README\.md$\|^tests/\|^\.playwright-mcp/\|^context-project/'

if [ "$ANTES" != "$DEPOIS" ]; then
    ARQUIVOS_ALTERADOS=$(git diff --name-only "$ANTES" "$DEPOIS")

    if echo "$ARQUIVOS_ALTERADOS" | grep -qv "$SEM_DEPLOY"; then
        # Existe mudança fora da lista — segue para o deploy abaixo.
        echo "🔧 Código/deployáveis alterados no pull — prosseguindo com deploy."
    else
        # Todos os arquivos estão na lista sem deploy. templates/ (bind
        # mount; Jinja2 recarrega sozinho) ainda precisa de rsync; docs e
        # testes (paths-ignore do GHCR) nunca publicam imagem para esse
        # commit — encerrar sem entrar no poll de 5 minutos.
        if echo "$ARQUIVOS_ALTERADOS" | grep -q '^templates/'; then
            echo "🎨 templates/ alterados — sincronizando com /srv/bc-sheet-processor/templates (sem deploy)."
            sudo rsync -a --delete templates/ /srv/bc-sheet-processor/templates/
        fi
        if echo "$ARQUIVOS_ALTERADOS" | grep -qv '^templates/'; then
            echo "ℹ️ Apenas arquivos sem deploy (docs/testes) — a imagem ${BRANCH}-<sha> não será publicada pelo GHCR."
            echo "   Nada a aplicar no Swarm."
        fi
        # Sinaliza ao wrapper (update-prod.sh) que nada foi deployado, para
        # ele pular o rsync redundante e imprimir um aviso explícito.
        # O próprio wrapper remove o marcador ao fim.
        touch .deploy-skipped
        echo "✅ Nada a deployar — concluído sem nova imagem."
        exit 0
    fi
fi

# Chega aqui quando: código/deployáveis alteradas no pull, OU nada novo no pull
# (re-aplicação/retry — ex.: git pull manual feito antes de rodar o script).
# Deploy da última versão sempre: TAG do ref remoto → espera GHCR → pre-pull → swap.
echo "🔧 Aplicando deploy da última versão (código alterado ou re-aplicação)..."

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

echo "✅ Deploy concluído!!"
