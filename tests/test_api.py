import asyncio
import shutil
from pathlib import Path

import httpx
import pytest

from bcsheetsprocessor.main import app
from bcsheetsprocessor.service import job_service

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _call(method: str, url: str, **kwargs) -> httpx.Response:
    async def _run():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
            return await ac.request(method, url, **kwargs)

    return asyncio.run(_run())


@pytest.fixture(autouse=True)
def _stub_processamento(monkeypatch):
    from bcsheetsprocessor.controller import upload_controller

    monkeypatch.setattr(
        upload_controller, "submit_processamento", lambda *args, **kwargs: None
    )


class TestUpload:
    def test_upload_xlsx_aceito(self, ambi_test):
        resp = _call(
            "POST",
            "/upload",
            files={"file": ("padrao3.xlsx", (FIXTURES / "padrao3.xlsx").read_bytes(),
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["job_id"]
        assert body["status_url"] == f"/status/{body['job_id']}"

    def test_upload_ods_aceito(self):
        resp = _call(
            "POST",
            "/upload",
            files={"file": ("padrao3.ods", (FIXTURES / "padrao3.ods").read_bytes(),
                            "application/vnd.oasis.opendocument.spreadsheet")},
        )
        assert resp.status_code == 200

    def test_upload_xls_aceito(self):
        resp = _call(
            "POST",
            "/upload",
            files={"file": ("padrao3.xls", (FIXTURES / "padrao3.xls").read_bytes(),
                            "application/vnd.ms-excel")},
        )
        assert resp.status_code == 200

    def test_upload_extensao_invalida(self):
        resp = _call(
            "POST",
            "/upload",
            files={"file": ("invalido.txt", (FIXTURES / "invalido.txt").read_bytes(),
                            "text/plain")},
        )
        assert resp.status_code == 400
        assert "Apenas arquivos de planilha" in resp.json()["detail"]

    def test_upload_sem_arquivo(self):
        resp = _call("POST", "/upload")
        assert resp.status_code in (400, 422)


class TestStatus:
    def test_status_job_existente(self, ambi_test):
        job_service.set_job_status("job-ok", {"status": "processing", "progresso": 10})
        resp = _call("GET", "/status/job-ok")
        assert resp.status_code == 200
        assert resp.json()["status"] == "processing"
        assert resp.json()["progresso"] == 10

    def test_status_job_inexistente(self):
        resp = _call("GET", "/status/nao-existe")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Job não encontrado"


class TestDownload:
    def test_download_antes_de_completar(self, ambi_test):
        job_service.set_job_status("job-proc", {"status": "processing"})
        resp = _call("GET", "/download/job-proc")
        assert resp.status_code == 400
        assert "Processamento ainda não finalizado" in resp.json()["detail"]

    def test_download_job_inexistente(self):
        resp = _call("GET", "/download/nao-existe")
        assert resp.status_code == 404

    def test_download_sem_caminho(self, ambi_test):
        job_service.set_job_status("job-sem-caminho", {"status": "completed"})
        resp = _call("GET", "/download/job-sem-caminho")
        assert resp.status_code == 500
        assert resp.json()["detail"] == "Caminho do arquivo não definido"

    def test_download_completo(self, ambi_test):
        destino = ambi_test["output_dir"] / "resultado.xlsx"
        shutil.copy(FIXTURES / "padrao3.xlsx", destino)
        job_service.set_job_status("job-done", {
            "status": "completed",
            "arquivo_saida": str(destino),
            "nome_arquivo": "resultado.xlsx",
        })
        resp = _call("GET", "/download/job-done")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert resp.content[:2] == b"PK"

    def test_download_arquivo_inexistente(self, ambi_test):
        destino = ambi_test["output_dir"] / "sumido.xlsx"
        job_service.set_job_status("job-sumido", {
            "status": "completed",
            "arquivo_saida": str(destino),
        })
        resp = _call("GET", "/download/job-sumido")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Arquivo não encontrado"