import os

import redis
import uvicorn


def redis_disponivel() -> bool:
    url = os.getenv("REDIS_URL", "redis://localhost:6379")
    try:
        r = redis.from_url(url, socket_connect_timeout=3, socket_timeout=3)
        r.ping()
        return True
    except Exception as e:
        print(f"[WORKERS] Falha ao checar Redis: {e}")
        return False


if __name__ == "__main__":
    workers = int(os.getenv("WORKERS", "2"))

    if not redis_disponivel():
        print(
            "✗ Redis indisponível — iniciando uvicorn com 1 worker (fallback). "
            "Com múltiplos workers o estado dos jobs não é compartilhado sem Redis."
        )
        workers = 1
    else:
        if workers > 1:
            print(f"✓ Redis conectado — iniciando uvicorn com {workers} workers")
        else:
            print(f"✓ Redis conectado — iniciando uvicorn com {workers} worker")

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "bcsheetsprocessor.main:app",
        host="0.0.0.0",
        port=port,
        workers=workers,
    )