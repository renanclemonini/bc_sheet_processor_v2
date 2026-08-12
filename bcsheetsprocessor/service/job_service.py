import json
import os

import redis

from bcsheetsprocessor.schema.job import JobStatus

redis_client = None
use_redis = False
jobs_status_fallback = {}

try:
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    use_redis = True
    print("✓ Redis conectado")
except Exception as e:
    print(f"✗ Redis indisponível: {e}")
    print("⚠ Usando memória local (não funciona com múltiplos workers)")
    use_redis = False
    jobs_status_fallback = {}


def get_job_status(job_id: str) -> JobStatus | None:
    if use_redis:
        data = redis_client.get(f"job:{job_id}")
        if data:
            return json.loads(data)
        return None
    return jobs_status_fallback.get(job_id)


def set_job_status(job_id: str, status_data: JobStatus):
    if use_redis:
        redis_client.setex(f"job:{job_id}", 3600, json.dumps(status_data))
    else:
        jobs_status_fallback[job_id] = status_data


def update_job_progress(job_id: str, progress: int):
    job = get_job_status(job_id)
    if job:
        job["progresso"] = progress
        set_job_status(job_id, job)