#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MODE=local
if [ "$#" -gt 0 ]; then MODE=$1; fi

case "$MODE" in
  local|sample|test)
    exec npm --prefix "$SCRIPT_DIR" run "$MODE"
    ;;
  *)
    echo "Usage: ./run.sh [local|sample|test]" >&2
    exit 2
    ;;
esac
