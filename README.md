# BC Sheet Processor

Excel spreadsheet processing system for normalizing BotConversa contact data.

## 🚀 Quick Start
```bash
# Clone the repository
git clone https://github.com/renanclemonini/bc_sheet_processor_v2.git bc_sheet_processor
cd bc_sheet_processor

# Build and start the application
docker-compose up -d --build

# Access http://localhost:8000
```

## 📋 Description

This system processes Excel spreadsheets from BotConversa imports, standardizing contact information such as name, phone, and tags. Processing is done asynchronously in the background, allowing simultaneous uploads and downloads.

## ✨ Features

- ✅ Upload Excel files (.xlsx, .xls, .ods)
- ✅ Asynchronous background processing
- ✅ Automatic phone normalization (special character removal)
- ✅ Full name separation into first name and last name
- ✅ Tag standardization
- ✅ Intuitive web interface with progress bar
- ✅ Processed file download
- ✅ Complete REST API

## 🚀 Technologies

- **FastAPI** - Modern and fast web framework
- **OpenPyXL** - Excel file processing (output)
- **Odfpy** - ODS file reading
- **Xlrd** - Legacy .xls file reading
- **Uvicorn** - High-performance ASGI server
- **Jinja2** - Template engine
- **Docker** - Application containerization

## 📦 Prerequisites

- Docker
- Docker Compose

## 🔧 Installation and Execution

### With Docker

1. Clone the repository:
```bash
git clone https://github.com/renanclemonini/bc_sheet_processor.git
cd bc_sheet_processor
```

2. Build and start the container:
```bash
docker-compose up -d --build
```

3. Access the application:
```
http://localhost:8000
```

### Useful commands

**Production (Docker Swarm) — scripts in `spa/spa-swarm/`:**
```bash
# Prepare the host (idempotent): swarm init + label + creates /srv (sudo) +
# creates the secrets from .env (read-only — never edits .env)
./spa/spa-swarm/swarm-init.sh

# Up/start service (docker stack deploy, with pre-flight and fast fail)
./spa/spa-swarm/service-up.sh

# Deploy (git pull + docker stack deploy with automatic immutable tag)
./spa/spa-swarm/deploy.sh

# Rebuild when the push already published a new image to GHCR; rsync of templates/
./spa/spa-swarm/rebuild.sh

# Optimized rebuild (recommended): TAG from origin/<branch> → waits for GHCR
# to publish → pre-pulls the image → stack deploy (minimal downtime, fast swap)
./spa/spa-swarm/new-rebuild.sh

# Post-deploy smoke test (2 uploads → status → download; generates n8n events)
./spa/spa-swarm/smoke-test.sh

# Stop service (docker stack rm)
./spa/spa-swarm/service-down.sh

# Tear everything down: stack rm + swarm leave --force
./spa/spa-swarm/swarm-leave.sh

# View logs
./spa/spa-swarm/logs.sh
```

**Local development (Docker Compose) — scripts in `spa/spa-compose/`:**
```bash
./spa/spa-compose/service-up.sh
./spa/spa-compose/logs.sh
```

### Operation — Docker Swarm (production)

The image is automatically published to `ghcr.io/renanclemonini/bc-sheet-processor`
by the `.github/workflows/docker-publish.yml` workflow on every push to `main`
(or `docker-swarm-migration` during the migration). Tags: `latest` + `<branch>-<sha>`.

First deploy on a new host (1 node):
```bash
# 1. Swarm init + label + /srv + secrets (idempotent). All automated:
#    creates /srv/bc-sheet-processor (sudo) and the bcsp_* secrets from .env.
#    If something fails (e.g., sudo without TTY), it shows the exact manual command.
./spa/spa-swarm/swarm-init.sh

# 2. Deploy the stack (service: bc_sheets_processor_swarm_sheet-processor)
./spa/spa-swarm/deploy.sh

# 3. (Optional) Post-deploy validation
./spa/spa-swarm/smoke-test.sh
```

Created secrets (the `bcsp_` prefix isolates them in the swarm):
`bcsp_redis_url`, `bcsp_n8n_webhook_user`, `bcsp_n8n_webhook_password` —
created by `swarm-init.sh` from `.env` (read-only; `.env` is never
modified by the script).

Future deploys (precise rollback on an immutable tag): the `<branch>-<sha>` tag
is automatically calculated after `git pull`; manual override remains valid:
```bash
export TAG=main-<sha>
./spa/spa-swarm/deploy.sh
```

Manual rollback: `docker service rollback bc_sheets_processor_swarm_sheet-processor`

1-node setup constraints: local bind mounts in `/srv/bc-sheet-processor`
(require the `node.labels.app` placement constraint), brief downtime on every
deploy (`mode: host` + `replicas: 1`, `stop-first` order) and automatic rollback
via healthcheck (`failure_action: rollback`).

## 📂 Folder Structure
```
bc_sheet_processor/
├── bcsheetsprocessor/   # Application package
│   ├── main.py          # FastAPI app (entry point)
│   ├── config.py        # Paths, templates and executor
│   ├── route/           # API routes (APIRouter)
│   │   ├── page_route.py    # GET /, GET /debug/headers
│   │   ├── upload_route.py  # POST /upload
│   │   └── result_route.py  # GET /status/{job_id}, GET /download/{job_id}
│   ├── controller/      # Request handling logic
│   │   ├── upload_controller.py
│   │   ├── status_controller.py
│   │   └── download_controller.py
│   ├── schema/          # Pydantic models and typed structures
│   │   ├── job.py
│   │   └── upload.py
│   └── service/         # Business logic (Excel processing, job status)
│       ├── job_service.py
│       └── excel_service.py
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker orchestration
├── .dockerignore       # Files ignored in build
├── entrypoint.sh       # Docker container entrypoint (referenced by Dockerfile)
├── run.py              # Launcher: decide workers based on Redis availability
├── spa/                # Operation scripts — spa-swarm/ (production Swarm) and spa-compose/ (local dev)
├── templates/          # HTML templates
│   └── index.html     # Upload interface
├── uploads/           # Temporary files (auto-created)
└── output/            # Processed files (auto-created)
```

## 📊 Spreadsheet Format

The system accepts two spreadsheet patterns, in `.xlsx`, `.xls` or `.ods` (LibreOffice) files.
The output is always `.xlsx` in Pattern 2.

### Pattern 1 (3 columns):
| Phone | Name | Tags |
|-------|------|------|
| 11987654321 | John Doe | Customer |

### Pattern 2 (4 columns):
| First name | Last name | Phone | Tags |
|------------|-----------|-------|------|
| John | Doe | 11987654321 | Customer |

**Notes:**
- Phones are automatically normalized
- Names are converted to Title Case format

## 📡 API Endpoints

### `GET /`
Web interface for file upload

### `POST /upload`
Upload spreadsheet file for processing (.xlsx, .xls, .ods)

**Request:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@spreadsheet.xlsx"
```

**Response:**
```json
{
  "success": true,
  "job_id": "abc123-def456-...",
  "message": "File uploaded! Processing started.",
  "status_url": "/status/abc123-def456-..."
}
```

### `GET /status/{job_id}`
Check processing status

**Response (Processing):**
```json
{
  "status": "processing",
  "arquivo_original": "spreadsheet.xlsx",
  "progresso": 45
}
```

**Response (Completed):**
```json
{
  "status": "completed",
  "arquivo_original": "spreadsheet.xlsx",
  "arquivo_saida": "/app/output/spreadsheet_processado.xlsx",
  "nome_arquivo": "spreadsheet_processado.xlsx",
  "progresso": 100,
  "resultado": {
    "linhas_originais": 1500,
    "colunas_originais": 4,
    "linhas_novo": 1450,
    "linhas_em_branco": 50,
    "colunas_em_branco": 0
  }
}
```

### `GET /download/{job_id}`
Download processed file

**Response:**
Excel file (.xlsx)

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs -f

# Rebuild container
docker-compose down
docker-compose up -d --build
```

### Volume permission errors
```bash
# Linux/Mac: adjust permissions
chmod -R 755 uploads output templates
```

### Port 8000 already in use
Edit `docker-compose.yml` and change the port:
```yaml
ports:
  - "8080:8000"  # Use port 8080 on host
```

### Clear temporary files
```bash
rm -rf uploads/* output/*
```

## 🛠️ Development

The container is configured for production with:
- 2 Uvicorn workers by default (configurable via `WORKERS` env var, e.g. `.env` or `docker-compose` environment)
- If Redis (`REDIS_URL`) is unavailable at startup, the app **automatically falls back to 1 worker** with an explicit log message (`✗ Redis indisponível — iniciando uvicorn com 1 worker`) — multi-worker requires Redis to share job status between processes
- Resource limits (CPU/Memory)
- Always restart automatically
- Health check configured

### Running tests
```bash
# Upload test via curl
curl -X POST "http://localhost:8000/upload" \
  -F "file=@example.xlsx"

# Check status
curl "http://localhost:8000/status/{job_id}"

# Download
curl -O -J "http://localhost:8000/download/{job_id}"
```

### Real-time logs
```bash
docker-compose logs -f sheet-processor
```

## 📝 Important Notes

- Temporary files are automatically removed after processing
- The system keeps job state in memory (restarting the container clears history)
- Rows without valid phone numbers are automatically discarded
- Phones with more than 13 digits are normalized by removing the 4th and 5th digits
- The `.dockerignore` keeps dev/docs artifacts (`.playwright-mcp/`, `*.txt`) out of the image

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/NewFeature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/NewFeature`)
5. Open a Pull Request

## 📄 License

This project is property of BotConversa.

## 👤 Author

**Renan Clemonini**
- GitHub: [@renanclemonini](https://github.com/renanclemonini)
- Company: BotConversa

## 📞 Support

For support, contact BotConversa's technical team at https://ajuda.botconversa.com.br/