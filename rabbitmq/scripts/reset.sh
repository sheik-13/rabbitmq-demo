#!/usr/bin/env bash
set -e

demo_dir=${1:?"Usage: ./scripts/reset.sh <demo-folder>"}
compose_file="$demo_dir/docker-compose.yml"

if [[ ! -f "$compose_file" ]]; then
  echo "No docker-compose.yml in $demo_dir" >&2
  exit 1
fi

echo "Removing $demo_dir broker data..."
docker compose -f "$compose_file" down -v
echo "Starting a clean broker..."
docker compose -f "$compose_file" up -d --wait
echo "Reset complete: http://localhost:15672 (guest/guest)"
