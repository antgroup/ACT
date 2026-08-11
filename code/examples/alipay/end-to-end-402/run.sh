#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MODE=${1:-local}

case "$MODE" in
  local|preview|test)
    exec npm --prefix "$SCRIPT_DIR" run "$MODE"
    ;;
  sandbox-preflight)
    exec npm --prefix "$SCRIPT_DIR" run sandbox:preflight
    ;;
  *)
    echo "Usage: ./run.sh [local|preview|test|sandbox-preflight]" >&2
    exit 2
    ;;
esac
