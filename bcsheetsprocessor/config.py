import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES_DIR = BASE_DIR / "templates"
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"

UPLOADS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
executor = ThreadPoolExecutor(max_workers=3)

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")
N8N_WEBHOOK_USER = os.getenv("N8N_WEBHOOK_USER", "")
N8N_WEBHOOK_PASSWORD = os.getenv("N8N_WEBHOOK_PASSWORD", "")