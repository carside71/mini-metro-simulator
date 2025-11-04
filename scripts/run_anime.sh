#!/usr/bin/env bash
# このスクリプトに渡した引数を、そのまま animation.py へ転送する
# 例: ./run_anime.sh --fps 30 --duration 60 --out /app/out/anim.mp4
set -euo pipefail
docker build -t mm-sim .
docker run --rm \
  -v "$PWD/out":/app/out \
  -e OUTPUT_DIR=/app/out \
  mm-sim \
  python anime.py "$@"