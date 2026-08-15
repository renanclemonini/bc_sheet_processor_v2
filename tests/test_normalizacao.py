from bcsheetsprocessor.service.excel_service import (
    detectar_padrao,
    linha_vazia,
    normalizar_etiquetas,
    normalizar_nome_completo,
    normalizar_nome_separado,
    normalizar_telefone,
)


class TestNormalizarNomeCompleto:
    def test_nome_simples(self):
        assert normalizar_nome_completo("maria silva") == ("Maria", "Silva")

    def test_nome_composto_sobrenome(self):
        assert normalizar_nome_completo("joão de souza") == ("João", "De Souza")

    def test_nome_unico(self):
        assert normalizar_nome_completo("ana") == ("Ana", "")

    def test_nome_vazio(self):
        assert normalizar_nome_completo("") == ("", "")

    def test_espacos_duplos(self):
        assert normalizar_nome_completo("  carlos   oliveira  ") == ("Carlos", "Oliveira")

    def test_nome_ja_maiusculo(self):
        assert normalizar_nome_completo("MARIA DA SILVA") == ("Maria", "Da Silva")


class TestNormalizarNomeSeparado:
    def test_primeiro_e_sobrenome(self):
        assert normalizar_nome_separado("maria", "silva") == ("Maria", "Silva")

    def test_primeiro_composto_concatena_ao_sobrenome(self):
        assert normalizar_nome_separado("joão de", "souza") == ("João", "De Souza")

    def test_sobrenome_vazio(self):
        assert normalizar_nome_separado("ana", "") == ("Ana", "")

    def test_primeiro_vazio(self):
        assert normalizar_nome_separado("", "oliveira") == ("", "Oliveira")


class TestNormalizarTelefone:
    def test_caracteres_especiais_removidos(self):
        assert normalizar_telefone("(12) 99812-3456") == "12998123456"

    def test_int(self):
        assert normalizar_telefone(12998123456) == "12998123456"

    def test_float_inteiro(self):
        assert normalizar_telefone(12998123456.0) == "12998123456"

    def test_none(self):
        assert normalizar_telefone(None) == ""

    def test_vazio(self):
        assert normalizar_telefone("") == ""

    def test_zeros_iniciais_removidos_acima_de_13(self):
        assert normalizar_telefone("005512998123456") == "5512998123456"

    def test_zeros_iniciais_mantidos_ate_13(self):
        assert normalizar_telefone("01299812345") == "01299812345"

    def test_menos_de_10_digitos(self):
        assert normalizar_telefone("12345678") == "12345678"


class TestNormalizarEtiquetas:
    def test_normal(self):
        assert normalizar_etiquetas("cliente") == "cliente"

    def test_nan_ignorado(self):
        assert normalizar_etiquetas("nan") == ""

    def test_nan_maiusculo(self):
        assert normalizar_etiquetas("NAN") == ""

    def test_none(self):
        assert normalizar_etiquetas(None) == ""

    def test_espacos(self):
        assert normalizar_etiquetas("  vip, importado  ") == "vip, importado"


class TestDetectarPadrao:
    def test_padrao_3_colunas(self):
        assert detectar_padrao(["telefone", "nome", "etiquetas"]) == (True, False)

    def test_padrao_3_colunas_plural(self):
        assert detectar_padrao(["telefones", "nomes", "tags"]) == (True, False)

    def test_padrao_3_colunas_acento_telefone_variantes(self):
        assert detectar_padrao(["contato", "nome", "etiqueta"]) == (True, False)

    def test_padrao_3_colunas_primeiro_nome(self):
        assert detectar_padrao(["primeiro nome", "telefone", "etiquetas"]) == (True, False)

    def test_padrao_3_colunas_primeiros_nomes_plural(self):
        assert detectar_padrao(["primeiros nomes", "contato", "tags"]) == (True, False)

    def test_padrao_3_colunas_numero_com_acento(self):
        assert detectar_padrao(["nome", "número", "etiquetas"]) == (True, False)

    def test_padrao_3_colunas_numero_sem_acento(self):
        assert detectar_padrao(["nomes", "numeros", "tags"]) == (True, False)

    def test_padrao_4_colunas(self):
        assert detectar_padrao(["primeiro nome", "sobrenome", "telefone", "etiquetas"]) == (False, True)

    def test_sem_padrao(self):
        assert detectar_padrao(["foo", "bar", "baz"]) == (False, False)

    def test_sem_padrao_parcial(self):
        assert detectar_padrao(["nome", "telefone"]) == (False, False)

    def test_headers_vazios(self):
        assert detectar_padrao([]) == (False, False)


class TestLinhaVazia:
    def test_vazia(self):
        assert linha_vazia([None, "", "  "]) is True

    def test_nao_vazia(self):
        assert linha_vazia([None, "x"]) is False

    def test_lista_vazia(self):
        assert linha_vazia([]) is True