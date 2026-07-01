# BC Sheet Processor

Excel spreadsheet processing system for normalizing BotConversa contact data.

## 🚀 Quick Start
```bash
# Clone the repository
git clone https://github.com/renanclemonini/bc_sheet_processor.git
cd bc_sheet_processor

# Build and start the application
docker-compose up -d --build

# Access http://localhost:8000
```

## 📋 Description

This system processes Excel spreadsheets from BotConversa imports, standardizing contact information such as name, phone, and tags. Processing is done asynchronously in the background, allowing simultaneous uploads and downloads.

## ✨ Features

- ✅ Upload Excel files (.xlsx, .xls)
- ✅ Asynchronous background processing
- ✅ Automatic phone normalization (special character removal)
- ✅ Full name separation into first name and last name
- ✅ Tag standardization
- ✅ Intuitive web interface with progress bar
- ✅ Processed file download
- ✅ Complete REST API

## 🚀 Technologies

- **FastAPI** - Modern and fast web framework
- **OpenPyXL** - Excel file processing
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
```bash
# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart

# Access container shell
docker-compose exec sheet-processor bash
```

## 📂 Folder Structure
```
bc_sheet_processor/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker orchestration
├── .dockerignore       # Files ignored in build
├── templates/          # HTML templates
│   └── index.html     # Upload interface
├── uploads/           # Temporary files (auto-created)
└── output/            # Processed files (auto-created)
```

## 📊 Spreadsheet Format

The system accepts two spreadsheet patterns:

### Pattern 1 (3 columns):
| Telefone | Nome | Etiquetas |
|----------|------|-----------|
| 11987654321 | John Doe | Customer |

### Pattern 2 (4 columns):
| Primeiro nome | Sobrenome | Telefone | Etiquetas |
|---------------|-----------|----------|-----------|
| John | Doe | 11987654321 | Customer |

**Notes:**
- Phones are automatically normalized
- Names are converted to Title Case format
- Default tag "NomeConfirmado" is automatically added

## 📡 API Endpoints

### `GET /`
Web interface for file upload

### `POST /upload`
Upload Excel file for processing

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
- 2 Uvicorn workers for better performance
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