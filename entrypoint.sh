#!/bin/ash
set -e

chown -R __USERNAME__:__USERNAME__ /home/__USERNAME__/uploads /home/__USERNAME__/output

exec su-exec __USERNAME__ poetry run python run.py
