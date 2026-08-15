# Instruções para agentes de IA

## Testes de backend

- Toda validação de backend deve ser feita via `poetry run pytest`.
- NÃO criar arquivos/planilhas temporárias nem simulações ad-hoc para testar manualmente (ex.: criar .xlsx no /tmp, rodar o pipeline isolado fora da suíte). Isso perde tempo e tokens desnecessários.
- A suíte existente já cobre upload/processamento/saída com fixtures (`tests/fixtures/`) e ambiente isolado (`tests/conftest.py`).
- Novos casos de teste: adicionar fixtures no gerador (`tests/fixtures/gerar_fixtures.py`) e/ou unit tests, depois rodar `poetry run pytest`.
