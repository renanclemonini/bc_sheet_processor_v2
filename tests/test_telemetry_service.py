from fastapi import Request

from bcsheetsprocessor.service.telemetry_service import (
    coletar_dados_request,
    enviar_log_para_n8n,
    extrair_marca_navegador,
)


class TestExtrairMarcaNavegador:
    def test_marca_normal(self):
        assert extrair_marca_navegador('"Not/A)Brand";v="8", "Google Chrome";v="128"') == "Google Chrome"

    def test_genericas_ignoradas(self):
        assert extrair_marca_navegador('"Not/A)Brand";v="8", "Chromium";v="128"') is None

    def test_apenas_genericas(self):
        assert extrair_marca_navegador('"Not/A)Brand";v="8"') is None

    def test_variante_antiga_ignorada(self):
        assert extrair_marca_navegador('"Not.A/Brand";v="99", "Chrome";v="128"') == "Chrome"

    def test_none(self):
        assert extrair_marca_navegador(None) is None

    def test_formato_invalido(self):
        assert extrair_marca_navegador("sem-versao") is None


def _request_fake(headers: dict) -> Request:
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/upload",
        "headers": [(k.lower().encode(), v.encode()) for k, v in headers.items()],
        "client": ("203.0.113.9", 1234),
        "query_string": b"",
        "scheme": "http",
        "server": ("test", 80),
        "root_path": "",
    }
    return Request(scope)


class TestColetarDadosRequest:
    def test_ip_cf_connecting_tem_prioridade(self):
        dados = coletar_dados_request(_request_fake({
            "CF-Connecting-IP": "8.8.8.8",
            "X-Forwarded-For": "9.9.9.9",
            "CF-IPCountry": "BR",
        }))
        assert dados["ip_address"] == "8.8.8.8"
        assert dados["country_code"] == "BR"

    def test_x_forwarded_for_como_fallback(self):
        dados = coletar_dados_request(_request_fake({"X-Forwarded-For": "9.9.9.9, 8.8.8.8"}))
        assert dados["ip_address"] == "9.9.9.9"

    def test_client_host_como_ultimo_fallback(self):
        dados = coletar_dados_request(_request_fake({}))
        assert dados["ip_address"] == "203.0.113.9"

    def test_chrome_desktop(self):
        dados = coletar_dados_request(_request_fake({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
        }))
        assert dados["device_type"] == "desktop"
        assert dados["browser_name"] == "Chrome"

    def test_celular(self):
        dados = coletar_dados_request(_request_fake({
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        }))
        assert dados["device_type"] == "mobile"

    def test_bot(self):
        dados = coletar_dados_request(_request_fake({
            "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        }))
        assert dados["is_bot"] is True
        assert dados["device_type"] == "bot"

    def test_sec_ch_ua_prioridade_sobre_user_agent(self):
        dados = coletar_dados_request(_request_fake({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
            "Sec-CH-UA": '"Not/A)Brand";v="8", "Google Chrome";v="128"',
        }))
        assert dados["browser_name"] == "Google Chrome"

    def test_metadados_basicos(self):
        dados = coletar_dados_request(_request_fake({"Content-Length": "1024"}))
        assert dados["method"] == "POST"
        assert dados["path"] == "/upload"
        assert dados["payload_size_bytes"] == 1024

    def test_content_length_invalido(self):
        dados = coletar_dados_request(_request_fake({"Content-Length": "abc"}))
        assert dados["payload_size_bytes"] == 0


class TestEnviarLogParaN8n:
    def test_sem_url_faz_nada(self):
        import asyncio

        asyncio.run(enviar_log_para_n8n({"job_id": "x"}))