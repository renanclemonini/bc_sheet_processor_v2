from fastapi import APIRouter, File, Request, UploadFile

from bcsheetsprocessor.controller import upload_controller

router = APIRouter(tags=["upload"])


@router.post("/upload")
async def upload_excel(request: Request, file: UploadFile = File(...)):
    """
    Recebe arquivo Excel, inicia processamento em background
    """
    return await upload_controller.processar_upload(file, request)
