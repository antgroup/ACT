#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

echo "[1/7] Repository integrity"
python3 scripts/check_repository.py

echo "[2/7] Public release snapshot"
python3 scripts/create_public_snapshot.py --check

echo "[3/7] A402 Candidate machine contracts"
python3 scripts/validate_a402_contract.py

echo "[4/7] Buyer Agent Quickstart"
npm --prefix code/examples/alipay/agent-payment test

echo "[5/7] End-to-end 402 inspector"
npm --prefix code/examples/alipay/end-to-end-402 test

echo "[6/7] Metered REST provider"
mvn -f code/examples/alipay/metered-rest-provider/pom.xml test

echo "[7/7] Sandbox showcase evidence validator"
npm --prefix code/web-client/alipay-ai-pay-showcase test
npm --prefix code/web-client/alipay-ai-pay-showcase run build

echo "All repository, Quickstart, and Demo checks passed."
