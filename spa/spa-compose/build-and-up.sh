#!/bin/bash

echo "Iniciando Build and UP"

#cd "$(dirname "$0")/../.."


docker compose up -d --build
sleep 10

echo "✅ Deploy concluído!!"
