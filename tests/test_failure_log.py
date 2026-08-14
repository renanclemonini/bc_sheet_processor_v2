import json
from pathlib import Path

from openpyxl.utils.exceptions import InvalidFileException

from bcsheetsprocessor.service.failure_log import (
    classificar_falha,
    registrar_falha,
)


class TestClassificacao:
    def test_formato_nao_reconhecido(self):
        exc = ValueError("Formato de planilha não reconhecido.\n\nColunas encontradas: foo, bar.")
        info = classificar_falha(exc)
        assert info.codigo == "formato_nao_reconhecido"
        assert info.categoria == "formato_invalido"
        assert "foo, bar" in info.mensagem_amigavel

    def test_nenhuma_linha_valida(self):
        exc = ValueError(
            "Nenhuma linha válida encontrada para processar.\n\nSOLUÇÃO: pressione F9"
        )
        info = classificar_falha(exc)
        assert info.codigo == "nenhuma_linha_valida"
        assert "F9" in info.mensagem_amigavel

    def test_arquivo_corrompido_openpyxl(self):
        info = classificar_falha(InvalidFileException("File is not a zip file"))
        assert info.codigo == "arquivo_corrompido"
        assert info.categoria == "arquivo_invalido"
        assert "corrompido" in info.mensagem_amigavel

    def test_arquivo_corrompido_badzip(self):
        info = classificar_falha(ValueError("BadZipFile: File is not a zip file"))
        assert info.codigo == "arquivo_corrompido"

    def test_arquivo_corrompido_xlrd(self):
        from xlrd import XLRDError

        info = classificar_falha(XLRDError("Expected BOF record; found not a valid xls"))
        assert info.codigo == "arquivo_corrompido"

    def test_erro_geracao_saida(self):
        info = classificar_falha(Exception("Arquivo não foi criado no sistema de arquivos"))
        assert info.codigo == "erro_geracao_saida"
        assert info.categoria == "erro_saida"

        info2 = classificar_falha(Exception("Arquivo gerado está corrompido: boom"))
        assert info2.codigo == "erro_geracao_saida"

    def test_fallback_erro_interno(self):
        info = classificar_falha(RuntimeError("algo completamente inesperado"))
        assert info.codigo == "erro_interno"
        assert info.categoria == "erro_interno"
        assert "inesperado" in info.mensagem_amigavel


class TestRegistrarFalha:
    def test_grava_jsonl_no_home(self, tmp_path, monkeypatch):
        from bcsheetsprocessor.service import failure_log

        home = tmp_path / "home"
        monkeypatch.setattr(failure_log, "LOG_DIR", home / "logs")
        monkeypatch.setattr(failure_log, "LOG_PATH", home / "logs" / "error-logs-sheets-processor.log")

        info = registrar_falha(
            "job-123",
            "planilha.xlsx",
            InvalidFileException("File is not a zip file"),
            estagio="leitura",
            colunas=["foo", "bar", ""],
        )
        assert info.codigo == "arquivo_corrompido"

        caminho = failure_log.LOG_PATH
        assert caminho.exists()
        linha = json.loads(caminho.read_text(encoding="utf-8"))

        assert linha["job_id"] == "job-123"
        assert linha["nome_arquivo"] == "planilha.xlsx"
        assert linha["estagio"] == "leitura"
        assert linha["categoria"] == "arquivo_invalido"
        assert linha["codigo"] == "arquivo_corrompido"
        assert linha["detalhe_tecnico"] == "File is not a zip file"
        assert linha["colunas_encontradas"] == ["foo", "bar"]
        assert "corrompido" in linha["mensagem_amigavel"]
        assert linha["timestamp"]

    def test_detalhe_tecnico_truncado(self, tmp_path, monkeypatch):
        from bcsheetsprocessor.service import failure_log

        home = tmp_path / "home"
        monkeypatch.setattr(failure_log, "LOG_DIR", home / "logs")
        monkeypatch.setattr(failure_log, "LOG_PATH", home / "logs" / "error-logs-sheets-processor.log")

        registrar_falha("job-1", "a.xlsx", Exception("x" * 10000), estagio="processamento")
        linha = json.loads(failure_log.LOG_PATH.read_text(encoding="utf-8"))
        assert len(linha["detalhe_tecnico"]) <= 503
        assert linha["detalhe_tecnico"].endswith("...")

    def test_falha_na_gravacao_nao_propaga(self, tmp_path, monkeypatch):
        from bcsheetsprocessor.service import failure_log

        monkeypatch.setattr(
            failure_log, "LOG_DIR", Path("/proc/nao-criavel")
        )
        monkeypatch.setattr(
            failure_log, "LOG_PATH", Path("/proc/nao-criavel/error-logs-sheets-processor.log")
        )

        import logging

        logging.disable(logging.CRITICAL)
        info = registrar_falha("job-2", "b.xlsx", ValueError("boom"), estagio="leitura")
        assert info.codigo == "erro_interno"