#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ENV_FILE=${ACT_ALIPAY_SELLER_ENV_FILE:-"$SCRIPT_DIR/.env"}
MODE=${1:-run}

usage() {
  echo "Usage: ./run.sh [init|test|package|run]"
  echo "  init     Create .env from .env.example without overwriting existing config"
  echo "  test     Run the local Maven test suite; no Alipay credentials required"
  echo "  package  Validate .env and build the runnable jar"
  echo "  run      Validate .env, build, and start the seller service (default)"
}

case "$MODE" in
  -h|--help|help)
    usage
    exit 0
    ;;
  init)
    if [ -e "$ENV_FILE" ]; then
      echo "Config already exists; not overwriting: $ENV_FILE"
      exit 0
    fi
    cp "$SCRIPT_DIR/.env.example" "$ENV_FILE"
    echo "Created $ENV_FILE"
    echo "Fill the official Alipay application, service, and key-file values before running ./run.sh."
    exit 0
    ;;
  test)
    command -v mvn >/dev/null 2>&1 || {
      echo "ERROR: Maven 3.8+ is required." >&2
      exit 1
    }
    exec mvn -f "$SCRIPT_DIR/pom.xml" test
    ;;
  package|run)
    ;;
  *)
    echo "ERROR: unknown mode: $MODE" >&2
    usage >&2
    exit 2
    ;;
esac

command -v java >/dev/null 2>&1 || {
  echo "ERROR: JDK 8+ is required." >&2
  exit 1
}
command -v mvn >/dev/null 2>&1 || {
  echo "ERROR: Maven 3.8+ is required." >&2
  exit 1
}

if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: seller config is missing: $ENV_FILE" >&2
  echo "Run './run.sh init', fill the official Alipay values, then run './run.sh'." >&2
  exit 2
fi

set -a
# shellcheck disable=SC1090
. "$ENV_FILE"
set +a

mvn -f "$SCRIPT_DIR/pom.xml" test package

if [ "$MODE" = "package" ]; then
  echo "Seller integration package is ready."
  exit 0
fi

exec java -jar "$SCRIPT_DIR/target/alipay-metered-rest-provider-0.1.0.jar"
