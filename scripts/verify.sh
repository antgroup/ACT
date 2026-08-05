#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

echo "[1/6] Repository integrity"
python3 scripts/check_repository.py

echo "[2/6] A402 Candidate machine contracts"
python3 scripts/validate_a402_contract.py

echo "[3/6] Buyer Agent Quickstart"
npm --prefix quickstarts/alipay/agent-payment test

echo "[4/6] End-to-end 402 inspector"
npm --prefix quickstarts/alipay/end-to-end-402 test

echo "[5/6] Metered REST provider"
mvn -f quickstarts/alipay/metered-rest-provider/pom.xml test

echo "[6/6] Sandbox showcase evidence validator"
npm --prefix demos/alipay-ai-pay-sandbox-showcase test
npm --prefix demos/alipay-ai-pay-sandbox-showcase run build

echo "All repository, Quickstart, and Demo checks passed."
