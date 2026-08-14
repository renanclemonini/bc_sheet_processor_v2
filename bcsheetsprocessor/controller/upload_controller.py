from uuid import uuid4

from fastapi import HTTPException, Request, UploadFile

from bcsheetsprocessor.config import UPLOADS_DIR
from bcsheetsprocessor.schema.upload import UploadResponse
from bcsheetsprocessor.service import job_service
from bcsheetsprocessor.service.excel_service import submit_processamento
from bcsheetsprocessor.service.telemetry_service import coletar_dados_request


async def processar_upload(file: UploadFile, request: Request) -> UploadResponse:
    if not file.filename.endswith((".xlsx", ".xls", ".ods")):
        raise HTTPException(
            400, detail="Apenas arquivos de planilha (.xlsx, .xls, .ods) são aceitos"
        )

    job_id = str(uuid4())

    temp_path = str(UPLOADS_DIR / f"{job_id}_{file.filename}")
    conteudo = await file.read()

    with open(temp_path, "wb") as f:
        f.write(conteudo)

    job_service.set_job_status(job_id, {
        "status": "processing",
        "arquivo_original": file.filename,
        "progresso": 0,
    })

    submit_processamento(temp_path, job_id, file.filename, coletar_dados_request(request))

    return UploadResponse(
        success=True,
        job_id=job_id,
        message="Arquivo enviado! Processamento iniciado.",
        status_url=f"/status/{job_id}",
    )