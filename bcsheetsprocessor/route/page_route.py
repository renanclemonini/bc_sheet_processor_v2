from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from bcsheetsprocessor.config import templates

router = APIRouter(tags=["páginas"])


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página principal com formulário de upload"""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/debug/headers")
async def debug_headers(request: Request):
    return dict(request.headers)