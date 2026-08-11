#!/bin/bash

echo "🚀 Iniciando deploy..."

cd ~/bc_sheet_processor

ANTES=$(git rev-parse HEAD)
git pull origin main
DEPOIS=$(git rev-parse HEAD)

if [ "$ANTES" == "$DEPOIS" ]; then
    echo "ℹ️  Nada novo para atualizar."
    exit 0
fi

ARQUIVOS_ALTERADOS=$(git diff --name-only "$ANTES" "$DEPOIS")

# Se só mudou algo dentro de templates/, não precisa rebuild nem restart
if echo "$ARQUIVOS_ALTERADOS" | grep -qv '^templates/'; then
    echo "🔧 Código ou dependências alteradas, rebuildando..."
    docker compose up -d --build
else
    echo "🎨 Só templates alterados — Jinja2 recarrega sozinho, sem rebuild."
fi

echo "✅ Deploy concluído!!"
