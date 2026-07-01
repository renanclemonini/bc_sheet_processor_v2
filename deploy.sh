#!/bin/bash

echo "🚀 Iniciando deploy..."

cd ~/bc_sheet_processor

git pull origin main

docker compose down

docker compose up -d --build

echo "✅ Deploy concluído!!"