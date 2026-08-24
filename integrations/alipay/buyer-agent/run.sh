#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MODE=${1:-preflight}

case "$MODE" in
  preflight)
    exec npm --prefix "$SCRIPT_DIR" run preflight
    ;;
  test)
    exec npm --prefix "$SCRIPT_DIR" test
    ;;
  *)
    echo "Usage: ./run.sh [preflight|test]" >&2
    exit 2
    ;;
esac
