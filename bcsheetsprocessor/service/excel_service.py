import asyncio
import os
import re
import unicodedata
from datetime import datetime, timezone
from uuid import uuid4

from openpyxl import Workbook, load_workbook

from bcsheetsprocessor.config import OUTPUT_DIR, executor
from bcsheetsprocessor.service import job_service
from bcsheetsprocessor.service.telemetry_service import enviar_log_para_n8n

COLUNAS_NOME = ("nome", "nomes")
COLUNAS_PRIMEIRO_NOME = ("primeiro nome", "primeiros nomes")
COLUNAS_SOBRENOME = ("sobrenome", "sobrenomes")
COLUNAS_TELEFONE = (
    "telefone",
    "telefones",
    "contato",
    "contatos",
    "celular",
    "celulares",
)
COLUNAS_ETIQUETAS = ("etiquetas", "etiqueta", "tag", "tags")
COLUNAS_IMPORTANTES = (
    COLUNAS_NOME + COLUNAS_PRIMEIRO_NOME + COLUNAS_SOBRENOME + COLUNAS_TELEFONE
)


def resolver_coluna(idx: dict, *variantes: str) -> int | None:
    """Retorna o índice da primeira variante encontrada (exato tem prioridade)"""
    for var in variantes:
        if var in idx:
            return idx[var]
    return None


def processar_excel_background(
    arquivo_entrada: str, job_id: str, nome_original: str, dados_request: dict, loop
):
    """
    Função que roda em thread separada
    Processa arquivo Excel e salva resultado
    """
    print(f"\n{'='*50}")
    print(f"INICIOU PROCESSAMENTO - Job ID: {job_id}")
    print(f"Arquivo: {arquivo_entrada}")
    print(f"{'='*50}\n")

    started_at = datetime.now(timezone.utc)

    payload_telemetria = {
        "job_id": job_id,
        "status": "failed",
        "arquivo_original": nome_original,
        "arquivo_saida_nome": None,
        "tamanho_saida_bytes": None,
        "colunas_encontradas": None,
        "linhas_originais": None,
        "colunas_originais": None,
        "linhas_novo": None,
        "linhas_em_branco": None,
        "colunas_em_branco": None,
        "erro_mensagem": None,
    }

    try:
        print(f"[{job_id}] Iniciando processamento de {nome_original}")

        headers = []

        # Lê o arquivo Excel com data_only=True para ignorar fórmulas e usar valores calculados
        with open(arquivo_entrada, "rb") as f:
            wb = load_workbook(f, data_only=True)
            ws = wb.active
            linhas_originais = ws.max_row
            colunas_originais = ws.max_column

            job_service.update_job_progress(job_id, 10)

            # Lê headers
            headers = [
                str(cell.value).strip().lower() if cell.value else ""
                for cell in next(ws.iter_rows(min_row=1, max_row=1))
            ]

            print(f"[{job_id}] ({len(headers)}) Colunas encontradas: {headers}")

            idx = {h: i for i, h in enumerate(headers)}
            novo_dados = []

            # Verifica padrão de colunas (aceita singular e plural)
            padrao_3_colunas = (
                resolver_coluna(idx, *COLUNAS_NOME) is not None
                and resolver_coluna(idx, *COLUNAS_TELEFONE) is not None
                and resolver_coluna(idx, *COLUNAS_ETIQUETAS) is not None
            )
            padrao_4_colunas = (
                resolver_coluna(idx, *COLUNAS_PRIMEIRO_NOME) is not None
                and resolver_coluna(idx, *COLUNAS_SOBRENOME) is not None
                and resolver_coluna(idx, *COLUNAS_TELEFONE) is not None
                and resolver_coluna(idx, *COLUNAS_ETIQUETAS) is not None
            )

            if not padrao_3_colunas and not padrao_4_colunas:
                colunas_str = ", ".join(s for s in headers if s) or "(nenhuma coluna com nome encontrada)"
                raise ValueError(
                    "Formato de planilha não reconhecido."
                    f"\n\nColunas encontradas: {colunas_str}."
                )

            linhas_em_branco = 0
            celulas_com_formula_sem_valor = 0
            linhas_com_problema = []

            col_nome = resolver_coluna(idx, *COLUNAS_NOME)
            col_primeiro_nome = resolver_coluna(idx, *COLUNAS_PRIMEIRO_NOME)
            col_sobrenome = resolver_coluna(idx, *COLUNAS_SOBRENOME)
            col_telefone = resolver_coluna(idx, *COLUNAS_TELEFONE)
            col_etiquetas = resolver_coluna(idx, *COLUNAS_ETIQUETAS)

            job_service.update_job_progress(job_id, 30)

            # Processa cada linha
            for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                # Pula linhas vazias
                if all(cell is None or str(cell).strip() == "" for cell in row):
                    linhas_em_branco += 1
                    continue

                # Detecta células None que podem ser fórmulas não calculadas
                tem_none_suspeito = False
                for col_idx, cell in enumerate(row):
                    if cell is None and col_idx < len(headers):
                        col_name = headers[col_idx]
                        # Verifica se é uma coluna importante
                        if col_name in COLUNAS_IMPORTANTES:
                            tem_none_suspeito = True
                            celulas_com_formula_sem_valor += 1
                            linhas_com_problema.append(row_idx)
                            break

                if tem_none_suspeito:
                    continue  # Pula essa linha

                primeiro_nome = ""
                sobrenome = ""
                telefone = ""
                etiquetas = ""

                # Processa nome (padrão 3 colunas: nome completo em uma coluna)
                if padrao_3_colunas:
                    nome = str(row[col_nome] or "").strip()
                    partes = nome.split()
                    primeiro_nome = partes[0].title() if partes else ""
                    sobrenome = " ".join(partes[1:]).title() if len(partes) > 1 else ""

                # Processa nome (padrão 4 colunas: nome e sobrenome separados)
                elif padrao_4_colunas:
                    primeiro = str(row[col_primeiro_nome] or "").strip()
                    sobrenome_original = str(row[col_sobrenome] or "").strip()

                    partes = primeiro.split()
                    primeiro_nome = partes[0].title() if partes else ""
                    sobrenome_splitado = (
                        " ".join(partes[1:]).title() if len(partes) > 1 else ""
                    )
                    sobrenome = (
                        f"{sobrenome_splitado} {sobrenome_original}".strip().title()
                    )

                # Processa telefone
                if col_telefone is not None and len(row) > col_telefone:
                    val_telefone = row[col_telefone]
                    if isinstance(val_telefone, float) and val_telefone.is_integer():
                        val_telefone = int(val_telefone)
                    telefone = str(val_telefone or "")
                    telefone = re.sub(r"\D", "", telefone)
                    if len(telefone) > 13 and telefone.startswith("0"):
                        telefone = telefone[1:]

                # Processa etiquetas
                if col_etiquetas is not None and len(row) > col_etiquetas:
                    etiqueta_padrao = ""
                    val = str(row[col_etiquetas] or "").strip()
                    etiquetas = (
                        f"{val}, {etiqueta_padrao}"
                        if val and val.lower() != "nan"
                        else etiqueta_padrao
                    )

                # Adiciona linha se tiver telefone válido
                if telefone and len(telefone) >= 10:
                    novo_dados.append([primeiro_nome, sobrenome, telefone, etiquetas])

                # Atualiza progresso a cada 1000 linhas
                if row_idx % 1000 == 0 and linhas_originais > 0:
                    progresso = 30 + int((row_idx / linhas_originais) * 50)
                    job_service.update_job_progress(job_id, min(progresso, 80))

            # Fecha o workbook original
            wb.close()

            print(f"[{job_id}] Processadas {len(novo_dados)} linhas válidas")

            # Aviso sobre fórmulas
            if celulas_com_formula_sem_valor > 0:
                print(f"[{job_id}] ⚠ AVISO: {celulas_com_formula_sem_valor} células com possíveis fórmulas não calculadas foram ignoradas")
                print(f"[{job_id}] ⚠ Linhas afetadas (primeiras 10): {linhas_com_problema[:10]}")

        # Conta colunas em branco (reabre o arquivo)
        colunas_em_branco = 0
        with open(arquivo_entrada, "rb") as f:
            wb = load_workbook(f, read_only=True, data_only=True)
            ws = wb.active

            for col_idx in range(colunas_originais):
                coluna_vazia = True
                for row in ws.iter_rows(
                    min_row=2,
                    min_col=col_idx + 1,
                    max_col=col_idx + 1,
                    values_only=True,
                ):
                    if row[0] is not None and str(row[0]).strip() != "":
                        coluna_vazia = False
                        break
                if coluna_vazia:
                    colunas_em_branco += 1

            wb.close()

        job_service.update_job_progress(job_id, 85)

        # Validação antes de criar arquivo
        if len(novo_dados) == 0:
            erro_msg = "Nenhuma linha válida encontrada para processar."
            if celulas_com_formula_sem_valor > 0:
                erro_msg += f"\n\nDetectadas {celulas_com_formula_sem_valor} células com possíveis fórmulas não calculadas."
                erro_msg += "\n\nSOLUÇÃO: Abra o arquivo no Excel, pressione F9 para recalcular todas as fórmulas, salve o arquivo e tente novamente."
            raise ValueError(erro_msg)

        print(f"[{job_id}] Criando novo arquivo Excel...")

        # Cria novo workbook
        wb_novo = Workbook()
        ws_novo = wb_novo.active
        ws_novo.title = "Contatos"

        # Adiciona cabeçalho
        ws_novo.append(["Primeiro nome", "Sobrenome", "Telefone", "Etiquetas"])

        # Adiciona dados
        for linha in novo_dados:
            ws_novo.append(linha)

        # Define nome e caminho do arquivo de saída
        nome_base = os.path.splitext(nome_original)[0]
        nome_base = unicodedata.normalize('NFKD', nome_base).encode('ascii', 'ignore').decode('ascii')
        nome_saida = f"{nome_base}_{uuid4()}.xlsx"
        caminho_saida = os.path.abspath(os.path.join(OUTPUT_DIR, nome_saida))

        print(f"[{job_id}] Salvando em: {caminho_saida}")

        # Garante que o diretório existe
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Salva o arquivo
        wb_novo.save(caminho_saida)
        wb_novo.close()

        # Verifica se o arquivo foi criado
        if not os.path.exists(caminho_saida):
            raise Exception("Arquivo não foi criado no sistema de arquivos")

        tamanho = os.path.getsize(caminho_saida)
        print(f"[{job_id}] ✓ Arquivo salvo: {tamanho} bytes")

        # Valida o arquivo Excel gerado
        try:
            wb_teste = load_workbook(caminho_saida, read_only=True)
            linhas_teste = wb_teste.active.max_row
            wb_teste.close()
            print(f"[{job_id}] ✓ Arquivo validado: {linhas_teste} linhas")
        except Exception as e:
            print(f"[{job_id}] ✗ AVISO: Arquivo pode estar corrompido: {str(e)}")
            raise Exception(f"Arquivo gerado está corrompido: {str(e)}")

        job_service.update_job_progress(job_id, 100)

        # Prepara mensagem de aviso se houver fórmulas
        aviso_formulas = None
        if celulas_com_formula_sem_valor > 0:
            aviso_formulas = f"{celulas_com_formula_sem_valor} células com possíveis fórmulas não calculadas foram ignoradas. Linhas afetadas: {', '.join(map(str, linhas_com_problema[:10]))}"
            if len(linhas_com_problema) > 10:
                aviso_formulas += f" e mais {len(linhas_com_problema) - 10}..."

        # Marca como concluído
        resultado = {
            "status": "completed",
            "arquivo_saida": caminho_saida,
            "nome_arquivo": nome_saida,
            "arquivo_original": nome_original,
            "progresso": 100,
            "resultado": {
                "linhas_originais": linhas_originais,
                "colunas_originais": colunas_originais,
                "colunas_encontradas": headers,
                "linhas_novo": len(novo_dados),
                "linhas_em_branco": linhas_em_branco,
                "colunas_em_branco": colunas_em_branco,
            },
        }

        if aviso_formulas:
            resultado["aviso_formulas"] = aviso_formulas

        payload_telemetria.update({
            "status": "completed",
            "arquivo_saida_nome": nome_saida,
            "tamanho_saida_bytes": tamanho,
            "colunas_encontradas": headers,
            "linhas_originais": linhas_originais,
            "colunas_originais": colunas_originais,
            "linhas_novo": len(novo_dados),
            "linhas_em_branco": linhas_em_branco,
            "colunas_em_branco": colunas_em_branco,
        })

        job_service.set_job_status(job_id, resultado)

        print(f"[{job_id}] ✓ Processamento concluído!")
        print(
            f"[{job_id}] Arquivo original: {linhas_originais} linhas x {colunas_originais} colunas"
        )
        print(f"[{job_id}] Novo arquivo: {len(novo_dados) + 1} linhas x 4 colunas")
        print(f"[{job_id}] Arquivo salvo em: {caminho_saida}")
        if aviso_formulas:
            print(f"[{job_id}] ⚠ {aviso_formulas}")

    except Exception as e:
        print(f"[{job_id}] ✗ Erro: {str(e)}")
        import traceback

        traceback.print_exc()

        payload_telemetria["erro_mensagem"] = str(e)

        job_service.set_job_status(job_id, {
            "status": "error",
            "error": str(e),
            "colunas_encontradas": headers,
            "arquivo_original": nome_original,
            "progresso": 0,
        })

    finally:
        payload_telemetria["duracao_ms"] = int(
            (datetime.now(timezone.utc) - started_at).total_seconds() * 1000
        )
        payload_telemetria["request"] = dados_request

        try:
            asyncio.run_coroutine_threadsafe(
                enviar_log_para_n8n(payload_telemetria), loop
            )
        except Exception as e:
            print(f"[TELEMETRY] Erro ao agendar envio para n8n: {e}")

        # Remove arquivo temporário
        if os.path.exists(arquivo_entrada):
            try:
                os.remove(arquivo_entrada)
                print(f"[{job_id}] Arquivo temporário removido")
            except Exception as e:
                print(f"[{job_id}] Erro ao remover temporário: {str(e)}")


def submit_processamento(temp_path: str, job_id: str, nome_original: str, dados_request: dict):
    loop = asyncio.get_event_loop()
    loop.run_in_executor(
        executor,
        processar_excel_background,
        temp_path,
        job_id,
        nome_original,
        dados_request,
        loop,
    )
