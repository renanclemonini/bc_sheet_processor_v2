import ipaddress

import httpx

from fastapi import Request
from user_agents import parse

from bcsheetsprocessor.config import (
    N8N_WEBHOOK_PASSWORD,
    N8N_WEBHOOK_URL,
    N8N_WEBHOOK_USER,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)


MARCAS_GENERICAS = {
    "not/a)brand",
    "not)a;brand",
    "not.a/brand",
    "chromium",
}


def normalizar_ip(raw_ip: str | None) -> str | None:
    """
    Extrai IPv4 quando o endereço vier no formato IPv4-mapped (::ffff:a.b.c.d).
    Para IPv6 nativo, não existe conversão real — retorna como veio.
    """
    if not raw_ip:
        return raw_ip

    try:
        ip_obj = ipaddress.ip_address(raw_ip)
    except ValueError:
        return raw_ip

    if isinstance(ip_obj, ipaddress.IPv6Address) and ip_obj.ipv4_mapped:
        return str(ip_obj.ipv4_mapped)

    return raw_ip


def extrair_marca_navegador(sec_ch_ua: str | None) -> str | None:
    """Extrai a primeira marca real do header sec-ch-ua, ignorando marcas genéricas."""
    if not sec_ch_ua:
        return None

    for parte in sec_ch_ua.split(","):
        if ";v=" not in parte:
            continue

        marca, _ = parte.strip().split(";v=", 1)
        marca = marca.strip().strip('"')

        if marca.lower() in MARCAS_GENERICAS:
            continue

        return marca

    return None


def coletar_dados_request(request: Request) -> dict:
    """Extrai dados do request para compor o access_log enviado ao n8n."""
    headers = request.headers

    ip_address = headers.get("cf-connecting-ip")

    if not ip_address:
        x_forwarded_for = headers.get("x-forwarded-for")

        if x_forwarded_for:
            ip_address = x_forwarded_for.split(",")[0].strip()

    if not ip_address and request.client:
        ip_address = request.client.host

    ip_address = normalizar_ip(ip_address)

    user_agent_raw = headers.get("user-agent", "") or ""
    ua = parse(user_agent_raw)

    if ua.is_bot:
        device_type = "bot"
    elif ua.is_tablet:
        device_type = "tablet"
    elif ua.is_mobile:
        device_type = "mobile"
    else:
        device_type = "desktop"

    try:
        payload_size = int(headers.get("content-length") or 0)
    except ValueError:
        payload_size = 0

    return {
        "cf_ray": headers.get("cf-ray"),
        "ip_address": ip_address,
        "country_code": headers.get("cf-ipcountry"),
        "user_agent": user_agent_raw or None,
        "browser_name": (
            extrair_marca_navegador(headers.get("sec-ch-ua"))
            or ua.browser.family
        ),
        "browser_version": ua.browser.version_string,
        "os_name": ua.os.family,
        "device_type": device_type,
        "is_bot": ua.is_bot,
        "accept_language": headers.get("accept-language"),
        "referer": headers.get("referer"),
        "method": request.method,
        "path": request.url.path,
        "payload_size_bytes": payload_size,
    }


async def enviar_log_para_n8n(payload: dict) -> None:
    """Envia payload de telemetria para o webhook do n8n. Nunca propaga exceção."""
    if not N8N_WEBHOOK_URL:
        print(
            "[TELEMETRY] N8N_WEBHOOK_URL nao configurada, envio ignorado"
        )
        return

    try:
        auth = None

        if N8N_WEBHOOK_USER and N8N_WEBHOOK_PASSWORD:
            auth = (N8N_WEBHOOK_USER, N8N_WEBHOOK_PASSWORD)

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                N8N_WEBHOOK_URL,
                json=payload,
                auth=auth,
            )

            response.raise_for_status()

        print(
            f"[TELEMETRY] Log enviado para n8n "
            f"(job {payload.get('job_id')})"
        )

    except httpx.HTTPError as e:
        print(
            f"[TELEMETRY] Erro HTTP ao enviar para n8n: {e}"
        )

    except Exception as e:
        print(
            f"[TELEMETRY] Erro ao enviar para n8n: {e}"
        )


async def enviar_log_para_telegram_bot(message: str) -> None:
    """Envia uma mensagem para o Telegram. Nunca propaga exceção."""
    if not TELEGRAM_BOT_TOKEN:
        print(
            "[TELEMETRY] TELEGRAM_BOT_TOKEN não configurado, "
            "envio ignorado"
        )
        return

    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": str(TELEGRAM_CHAT_ID),
        "text": message,
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                url,
                json=payload,
            )

            response.raise_for_status()

        print("[TELEMETRY] Relatório enviado para Telegram")

    except httpx.HTTPError as e:
        print(
            f"[TELEMETRY] Erro HTTP ao enviar para Telegram: {e}"
        )

    except Exception as e:
        print(
            f"[TELEMETRY] Erro ao enviar para Telegram: {e}"
        )


def formatar_tamanho_bytes(tamanho_bytes: int) -> str:
    """Converte bytes para uma unidade mais legível."""
    if tamanho_bytes < 1024:
        return f"{tamanho_bytes} B"

    if tamanho_bytes < 1024 * 1024:
        return f"{tamanho_bytes / 1024:.2f} KB"

    return f"{tamanho_bytes / (1024 * 1024):.2f} MB"


def gerar_relatorio_telegram(payload: dict) -> str:
    """Transforma o payload de telemetria em um relatório legível."""

    status = payload.get("status")
    job_id = payload.get("job_id")
    arquivo_original = payload.get("arquivo_original", "-")

    duracao_ms = payload.get("duracao_ms")

    if duracao_ms is not None:
        duracao = f"{duracao_ms / 1000:.2f}s"
    else:
        duracao = "-"

    request_data = payload.get("request") or {}

    # Dados da requisição
    ip_address = request_data.get("ip_address") or "-"
    country_code = request_data.get("country_code") or "-"
    browser_name = request_data.get("browser_name") or "-"
    browser_version = request_data.get("browser_version") or "-"
    os_name = request_data.get("os_name") or "-"
    device_type = request_data.get("device_type") or "-"
    is_bot = request_data.get("is_bot")

    if is_bot is True:
        bot_status = "Sim"
    elif is_bot is False:
        bot_status = "Não"
    else:
        bot_status = "-"

    accept_language = request_data.get("accept_language") or "-"
    referer = request_data.get("referer") or "-"
    method = request_data.get("method") or "-"
    path = request_data.get("path") or "-"
    cf_ray = request_data.get("cf_ray") or "-"
    payload_size = formatar_tamanho_bytes(
        request_data.get("payload_size_bytes") or 0
    )

    dados_request = (
        "\n\n"
        "🌐 REQUISIÇÃO\n"
        f"• IP: {ip_address}\n"
        f"• País: {country_code}\n"
        f"• Navegador: {browser_name} {browser_version}\n"
        f"• Sistema: {os_name}\n"
        f"• Dispositivo: {device_type}\n"
        f"• Bot: {bot_status}\n"
        f"• Idioma: {accept_language}\n"
        f"• Método: {method}\n"
        f"• Rota: {path}\n"
        f"• Payload: {payload_size}\n"
        f"• Referer: {referer}\n"
        f"• CF-Ray: {cf_ray}"
    )

    if status == "completed":
        linhas_originais = payload.get("linhas_originais", 0)
        linhas_novo = payload.get("linhas_novo", 0)
        linhas_em_branco = payload.get("linhas_em_branco", 0)
        linhas_telefone_invalido = payload.get(
            "linhas_telefone_invalido",
            0,
        )
        colunas_originais = payload.get("colunas_originais", 0)
        colunas_em_branco = payload.get("colunas_em_branco", 0)

        tamanho_saida = payload.get("tamanho_saida_bytes") or 0
        tamanho_formatado = formatar_tamanho_bytes(tamanho_saida)

        arquivo_saida = payload.get(
            "arquivo_saida_nome",
            "-",
        )

        relatorio = (
            "✅ PROCESSAMENTO CONCLUÍDO\n"
            "\n"
            f"📋 Job: {job_id}\n"
            f"📁 Arquivo: {arquivo_original}\n"
            f"📤 Saída: {arquivo_saida}\n"
            f"⏱️ Duração: {duracao}\n"
            "\n"
            "📊 RESULTADO\n"
            f"• Linhas originais: {linhas_originais}\n"
            f"• Linhas processadas: {linhas_novo}\n"
            f"• Linhas em branco: {linhas_em_branco}\n"
            f"• Telefones inválidos: {linhas_telefone_invalido}\n"
            f"• Colunas originais: {colunas_originais}\n"
            f"• Colunas em branco: {colunas_em_branco}\n"
            f"• Tamanho do arquivo: {tamanho_formatado}"
        )

        if payload.get("aviso_formulas"):
            relatorio += (
                "\n\n"
                "⚠️ AVISO\n"
                f"{payload['aviso_formulas']}"
            )

        relatorio += dados_request

        return relatorio

    erro = payload.get(
        "erro_mensagem",
        "Erro não informado",
    )

    return (
        "❌ PROCESSAMENTO FALHOU\n"
        "\n"
        f"📋 Job: {job_id}\n"
        f"📁 Arquivo: {arquivo_original}\n"
        f"⏱️ Duração: {duracao}\n"
        "\n"
        "🚨 ERRO\n"
        f"{erro}"
        f"{dados_request}"
    )
