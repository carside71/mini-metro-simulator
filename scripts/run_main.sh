#!/usr/bin/env bash
docker build -t mm-sim .
docker run --rm \
  -v "$PWD/out":/app/out \
  -e OUTPUT_DIR=/app/out \
  mm-sim