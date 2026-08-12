from typing import Optional, TypedDict


class JobResult(TypedDict):
    linhas_originais: int
    colunas_originais: int
    colunas_encontradas: list[str]
    linhas_novo: int
    linhas_em_branco: int
    colunas_em_branco: int


class JobStatus(TypedDict, total=False):
    status: str
    progresso: int
    arquivo_original: Optional[str]
    arquivo_saida: Optional[str]
    nome_arquivo: Optional[str]
    resultado: Optional[JobResult]
    aviso_formulas: Optional[str]
    error: Optional[str]
    colunas_encontradas: Optional[list[str]]