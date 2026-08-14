import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

os_reset = None


@pytest.fixture(autouse=True)
def ambi_test(tmp_path, monkeypatch):
    """Isola o ambiente: job state em memória, diretórios temporários, telemetria off."""
    from bcsheetsprocessor.service import job_service

    monkeypatch.setattr(job_service, "use_redis", False)
    monkeypatch.setattr(job_service, "jobs_status_fallback", {})
    job_service.jobs_status_fallback.clear()

    from bcsheetsprocessor.service import excel_service, telemetry_service
    from bcsheetsprocessor.controller import upload_controller

    out_dir = tmp_path / "output"
    up_dir = tmp_path / "uploads"
    out_dir.mkdir()
    up_dir.mkdir()

    monkeypatch.setattr(excel_service, "OUTPUT_DIR", out_dir)
    monkeypatch.setattr(upload_controller, "UPLOADS_DIR", up_dir)
    monkeypatch.setattr(telemetry_service, "N8N_WEBHOOK_URL", "")
    return {"output_dir": out_dir, "uploads_dir": up_dir}


@pytest.fixture
def loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


def rodar_processamento(amb, arquivo, nome_original=None, loop=None):
    """Executa processar_excel_background de forma síncrona (cópia temporária) e retorna o job.

    O processamento apaga o arquivo de entrada no finally, então o arquivo original
    (fixture committada) é copiado para o diretório de uploads temporário antes.
    """
    import shutil
    import uuid
    from pathlib import Path

    from bcsheetsprocessor.service import excel_service, job_service

    if loop is None:
        loop = asyncio.new_event_loop()

    job_id = str(uuid.uuid4())
    destino = amb["uploads_dir"] / f"{job_id}_{Path(arquivo).name}"
    shutil.copy(arquivo, destino)
    job_service.set_job_status(job_id, {"status": "processing", "progresso": 0})
    excel_service.processar_excel_background(
        str(destino), job_id, nome_original or Path(arquivo).name, {}, loop
    )

    async def _drenar():
        tarefas = [t for t in asyncio.all_tasks(loop) if t is not asyncio.current_task()]
        if tarefas:
            await asyncio.gather(*tarefas, return_exceptions=True)

    loop.run_until_complete(_drenar())
    loop.close()
    return job_id, job_service.get_job_status(job_id)


@pytest.fixture
def fixture_path():
    def _get(nome: str) -> Path:
        return FIXTURES_DIR / nome

    return _get