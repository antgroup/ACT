#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

echo "[1/10] Repository integrity"
python3 tools/quality/check_repository.py

echo "[2/10] Public release snapshot"
python3 tools/quality/create_public_snapshot.py --check

echo "[3/10] A402 implementation artifacts"
python3 tools/a402/validate_contract.py

echo "[4/10] TSD-CRD implementation artifacts"
python3 tools/tsd-crd/validate_contract.py

echo "[5/10] Product-neutral A402 sample"
npm --prefix code/samples/local-a402 test

echo "[6/10] TSD-CRD reference implementation"
npm --prefix code/samples/tsd-crd-reference run check

echo "[7/10] Alipay buyer integration"
npm --prefix integrations/alipay/buyer-agent test

echo "[8/10] Alipay seller integration"
mvn -f integrations/alipay/seller-java/pom.xml test

echo "[9/10] Alipay validation tools"
node --test integrations/alipay/validation/*.test.mjs

echo "[10/10] Machine payment showcase"
npm --prefix code/web-client/alipay-ai-pay-showcase test
npm --prefix code/web-client/alipay-ai-pay-showcase run build

echo "All repository checks passed."
