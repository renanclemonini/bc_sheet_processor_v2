from fastapi import APIRouter

from bcsheetsprocessor.controller import download_controller, status_controller

router = APIRouter(tags=["resultado"])


@router.get("/status/{job_id}")
async def verificar_status(job_id: str):
    """Verifica status do processamento"""
    return status_controller.verificar(job_id)


@router.get("/download/{job_id}")
async def download_arquivo(job_id: str):
    """
    Faz download do arquivo processado
    """
    return download_controller.download(job_id)