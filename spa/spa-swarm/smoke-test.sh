#!/bin/bash
set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

BASE_URL="${BASE_URL:-http://localhost:8000}"
TMPDIR="$(mktemp -d /tmp/smoke-test.XXXXXX)"
PYTHON_BIN=""

echo -e "🧪 Smoke test do BC Sheet Processor — ${BASE_URL}\n"

# --- 1. Python + openpyxl para gerar os arquivos de teste ---
if [ -x .venv/bin/python ] && .venv/bin/python -c "import openpyxl" 2>/dev/null; then
    PYTHON_BIN=".venv/bin/python"
elif python3 -c "import openpyxl" 2>/dev/null; then
    PYTHON_BIN="python3"
else
    echo -e "${RED}❌ openpyxl não encontrado. Instale ou rode de um diretório com .venv:${NC}"
    echo "   pip install openpyxl   # ou: poetry install"
    rm -rf "$TMPDIR"
    exit 1
fi

# --- 2. Gera 2 planilhas (padrões de 3 e 4 colunas), 1500 linhas cada ---
"$PYTHON_BIN" - "$TMPDIR" <<'EOF'
import sys
from openpyxl import Workbook

tmp = sys.argv[1]

w = Workbook()
ws = w.active
ws.append(["Telefone", "Nome", "Etiquetas"])
for i in range(1500):
    ws.append([f"(11) 98765-{i:04d}", f"joao da silva {i}", "cliente vip"])
w.save(f"{tmp}/smoke_3col.xlsx")

w2 = Workbook()
ws2 = w2.active
ws2.append(["Primeiro nome", "Sobrenome", "Telefone", "Etiquetas"])
for i in range(1500, 3000):
    ws2.append(["ANA", f"SOUZA {i}", f"11 91234-{i % 10000:04d}", "lead"])
w2.save(f"{tmp}/smoke_4col.xlsx")
print("ok")
EOF

echo -e "${GREEN}✅ Planilhas de teste geradas (smoke_3col.xlsx, smoke_4col.xlsx)${NC}"

# --- 3. Uploads simultâneos ---
curl -s -X POST "$BASE_URL/upload" -F "file=@$TMPDIR/smoke_3col.xlsx" > "$TMPDIR/resp1.json" &
curl -s -X POST "$BASE_URL/upload" -F "file=@$TMPDIR/smoke_4col.xlsx" > "$TMPDIR/resp2.json" &
wait

JOB1=$(python3 -c "import json;print(json.load(open('$TMPDIR/resp1.json'))['job_id'])" 2>/dev/null || true)
JOB2=$(python3 -c "import json;print(json.load(open('$TMPDIR/resp2.json'))['job_id'])" 2>/dev/null || true)

if [ -z "$JOB1" ] || [ -z "$JOB2" ]; then
    echo -e "${RED}❌ Upload falhou. Respostas:${NC}"
    cat "$TMPDIR/resp1.json" "$TMPDIR/resp2.json"
    rm -rf "$TMPDIR"
    exit 1
fi
echo -e "${GREEN}✅ Uploads aceitos: JOB1=$JOB1, JOB2=$JOB2${NC}"

# --- 4. Polling de /status até completed ---
PASS=0
for JOB in "$JOB1" "$JOB2"; do
    for i in $(seq 1 45); do
        S=$(curl -s "$BASE_URL/status/$JOB")
        case "$S" in
            *'"status":"completed"'*) echo -e "${GREEN}✅ $JOB: completed${NC}"; PASS=$((PASS+1)); break ;;
            *'"status":"error"'*)     echo -e "${RED}❌ $JOB: error — $S${NC}"; break ;;
        esac
        sleep 2
    done
    if ! echo "$S" | grep -q '"status":"completed"'; then
        echo -e "${RED}❌ $JOB: timeout aguardando completed.${NC}"
    fi
done

# --- 5. Downloads ---
if [ "$PASS" -eq 2 ]; then
    for JOB in "$JOB1" "$JOB2"; do
        CODE=$(curl -s -o "$TMPDIR/dl_$JOB.xlsx" -w "%{http_code}" "$BASE_URL/download/$JOB")
        SIZE=$(stat -c%s "$TMPDIR/dl_$JOB.xlsx" 2>/dev/null || echo 0)
        if [ "$CODE" -eq 200 ] && [ "$SIZE" -gt 1000 ]; then
            echo -e "${GREEN}✅ Download $JOB: HTTP $CODE, $SIZE bytes${NC}"
        else
            echo -e "${RED}❌ Download $JOB: HTTP $CODE, $SIZE bytes${NC}"
            PASS=0
        fi
    done
fi

# --- 6. Limpeza e resumo ---
rm -rf "$TMPDIR"

echo ""
echo -e "${YELLOW}Notas:${NC}"
echo "  • Este teste gerou 2 eventos de telemetria no n8n (arquivos smoke_*)."
echo "  • Arquivos processados ficam em /srv/bc-sheet-processor/output/ — limpe manualmente:"
echo "    sudo rm -f /srv/bc-sheet-processor/output/smoke_*"

if [ "$PASS" -eq 2 ]; then
    echo -e "${GREEN}✅ SMOKE TEST: PASS${NC}"
    exit 0
else
    echo -e "${RED}❌ SMOKE TEST: FAIL${NC}"
    exit 1
fi