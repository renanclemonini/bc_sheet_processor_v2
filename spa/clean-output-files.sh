#!/bin/bash
set -euo pipefail

OUTPUT_DIR="/home/renan/sheets-processor/output"

if [ ! -d "$OUTPUT_DIR" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Erro: diretório '$OUTPUT_DIR' não encontrado."
    exit 1
fi

TOTAL=$(find "$OUTPUT_DIR" -maxdepth 1 -type f | wc -l)

if [ "$TOTAL" -eq 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Nenhum arquivo para remover."
    exit 0
fi

find "$OUTPUT_DIR" -maxdepth 1 -type f -delete

echo "$(date '+%Y-%m-%d %H:%M:%S') - $TOTAL arquivo(s) removido(s) de $OUTPUT_DIR."