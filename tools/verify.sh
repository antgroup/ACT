#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

echo "[1/8] Repository integrity"
python3 tools/quality/check_repository.py

echo "[2/8] Public release snapshot"
python3 tools/quality/create_public_snapshot.py --check

echo "[3/8] A402 implementation artifacts"
python3 tools/a402/validate_contract.py

echo "[4/8] Product-neutral A402 sample"
npm --prefix code/samples/local-a402 test

echo "[5/8] Alipay buyer integration"
npm --prefix integrations/alipay/buyer-agent test

echo "[6/8] Alipay seller integration"
mvn -f integrations/alipay/seller-java/pom.xml test

echo "[7/8] Alipay validation tools"
node --test integrations/alipay/validation/*.test.mjs

echo "[8/8] Machine payment showcase"
npm --prefix code/web-client/alipay-ai-pay-showcase test
npm --prefix code/web-client/alipay-ai-pay-showcase run build

echo "All repository checks passed."
