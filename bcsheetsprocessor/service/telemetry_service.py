import httpx
from fastapi import Request
from user_agents import parse

from bcsheetsprocessor.config import (
    N8N_WEBHOOK_PASSWORD,
    N8N_WEBHOOK_URL,
    N8N_WEBHOOK_USER,
)

MARCAS_GENERICAS = {"not/a)brand", "not)a;brand", "not.a/brand", "chromium"}


def extrair_marca_navegador(sec_ch_ua: str | None) -> str | None:
    """Extrai a primeira marca real do header sec-ch-ua, ignorando marcas genéricas"""
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
    """Extrai dados do request para compor o access_log enviado ao n8n"""
    headers = request.headers

    ip_address = headers.get("cf-connecting-ip")
    if not ip_address:
        x_forwarded_for = headers.get("x-forwarded-for")
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(",")[0].strip()
    if not ip_address and request.client:
        ip_address = request.client.host

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
        "browser_name": extrair_marca_navegador(headers.get("sec-ch-ua")) or ua.browser.family,
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
        print("[TELEMETRY] N8N_WEBHOOK_URL nao configurada, envio ignorado")
        return

    try:
        auth = None
        if N8N_WEBHOOK_USER and N8N_WEBHOOK_PASSWORD:
            auth = (N8N_WEBHOOK_USER, N8N_WEBHOOK_PASSWORD)

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(N8N_WEBHOOK_URL, json=payload, auth=auth)
            response.raise_for_status()

        print(f"[TELEMETRY] Log enviado para n8n (job {payload.get('job_id')})")
    except httpx.HTTPError as e:
        print(f"[TELEMETRY] Erro HTTP ao enviar para n8n: {e}")
    except Exception as e:
        print(f"[TELEMETRY] Erro ao enviar para n8n: {e}")