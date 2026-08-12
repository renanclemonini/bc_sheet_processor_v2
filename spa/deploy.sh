#!/bin/bash

echo "🚀 Iniciando deploy..."

cd "$(dirname "$0")/.."

git pull origin main

docker compose down

docker compose up -d --build

echo "✅ Deploy concluído!!"