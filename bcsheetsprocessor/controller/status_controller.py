from fastapi import HTTPException

from bcsheetsprocessor.schema.job import JobStatus
from bcsheetsprocessor.service import job_service


def verificar(job_id: str) -> JobStatus:
    print(f"[STATUS] Verificando job: {job_id}")

    job = job_service.get_job_status(job_id)

    if not job:
        print(f"[STATUS] Job {job_id} NÃO ENCONTRADO!")
        raise HTTPException(404, detail="Job não encontrado")

    print(f"[STATUS] Status do job {job_id}: {job}")
    return job