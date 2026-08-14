import json
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path.home() / "logs"
LOG_PATH = LOG_DIR / "error-logs-sheets-processor.log"
DETALHE_TECNICO_MAX = 500

_lock = threading.Lock()

FORMATO_NAO_RECONHECIDO = "Formato de planilha não reconhecido"


@dataclass(frozen=True)
class FalhaInfo:
    codigo: str
    categoria: str
    mensagem_amigavel: str


def _eh_arquivo_corrompido(exc: Exception) -> bool:
    nome = type(exc).__name__
    if nome in ("InvalidFileException", "BadZipFile", "XLRDError"):
        return True
    mod = type(exc).__module__ or ""
    if "odf" in mod or "zipfile" in mod or "ElementTree" in mod or "xml" in mod:
        return True
    msg = str(exc).lower()
    return any(
        p in msg
        for p in (
            "not a zip file",
            "not an excel",
            "corrupt",
            "arquivo inexistente",
            "no such file",
            "was not found",
        )
    )


def _eh_erro_saida(exc: Exception) -> bool:
    msg = str(exc)
    return msg.startswith(
        ("Arquivo não foi criado no sistema de arquivos", "Arquivo gerado está corrompido")
    )


def classificar_falha(exc: Exception) -> FalhaInfo:
    """Classifica uma exceção de processamento em códigos/categorias conhecidos.

    Retorna sempre uma FalhaInfo — exceções desconhecidas caem no fallback erro_interno.
    """
    msg = str(exc)

    if msg.startswith(FORMATO_NAO_RECONHECIDO):
        return FalhaInfo(
            codigo="formato_nao_reconhecido",
            categoria="formato_invalido",
            mensagem_amigavel=msg,
        )

    if msg.startswith("Nenhuma linha válida"):
        return FalhaInfo(
            codigo="nenhuma_linha_valida",
            categoria="sem_linhas_validas",
            mensagem_amigavel=msg,
        )

    if _eh_erro_saida(exc):
        return FalhaInfo(
            codigo="erro_geracao_saida",
            categoria="erro_saida",
            mensagem_amigavel=(
                "Não foi possível gerar o arquivo de saída. "
                "Tente novamente; se o problema persistir, informe o suporte."
            ),
        )

    if _eh_arquivo_corrompido(exc):
        return FalhaInfo(
            codigo="arquivo_corrompido",
            categoria="arquivo_invalido",
            mensagem_amigavel=(
                "O arquivo está corrompido ou não é uma planilha válida "
                "(.xlsx, .xls ou .ods). Reexporte a planilha no Excel ou "
                "LibreOffice e tente novamente."
            ),
        )

    return FalhaInfo(
        codigo="erro_interno",
        categoria="erro_interno",
        mensagem_amigavel=(
            "Ocorreu um erro inesperado durante o processamento. "
            "Tente novamente; se o problema persistir, informe o suporte."
        ),
    )


def registrar_falha(
    job_id: str,
    nome_arquivo: str,
    exc: Exception,
    estagio: str,
    colunas: list | None = None,
) -> FalhaInfo:
    """Classifica a falha, grava uma linha JSONL e retorna o FalhaInfo.

    Nunca propaga exceção (padrão da telemetria) — se a gravação falhar, só loga no stdout.
    """
    info = classificar_falha(exc)

    detalhe = str(exc)
    if len(detalhe) > DETALHE_TECNICO_MAX:
        detalhe = detalhe[:DETALHE_TECNICO_MAX] + "..."

    linha = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "job_id": job_id,
        "nome_arquivo": nome_arquivo,
        "estagio": estagio,
        "categoria": info.categoria,
        "codigo": info.codigo,
        "mensagem_amigavel": info.mensagem_amigavel,
        "detalhe_tecnico": detalhe,
        "colunas_encontradas": [c for c in (colunas or []) if c],
    }

    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with _lock:
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(linha, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[FAILURE_LOG] Erro ao gravar log de falha: {e}")

    return info