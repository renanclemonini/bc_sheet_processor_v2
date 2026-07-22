#!/bin/ash
set -e

chown -R __USERNAME__:__USERNAME__ /home/__USERNAME__/uploads /home/__USERNAME__/output

exec su-exec __USERNAME__ poetry run uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
