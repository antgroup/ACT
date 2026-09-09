#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

echo "[1/11] Repository integrity"
python3 tools/quality/check_repository.py

echo "[2/11] Public release snapshot"
python3 tools/quality/create_public_snapshot.py --check

echo "[3/11] Key official external links"
python3 tools/quality/check_external_links.py

echo "[4/11] A402 implementation artifacts"
python3 tools/a402/validate_contract.py

echo "[5/11] TSD-CRD implementation artifacts"
python3 tools/tsd-crd/validate_contract.py

echo "[6/11] Product-neutral A402 sample"
npm --prefix code/samples/local-a402 test

echo "[7/11] TSD-CRD reference implementation"
npm --prefix code/samples/tsd-crd-reference run check

echo "[8/11] Alipay buyer integration"
npm --prefix integrations/alipay/buyer-agent test

echo "[9/11] Alipay seller integration"
mvn -f integrations/alipay/seller-java/pom.xml test

echo "[10/11] Alipay validation tools"
node --test integrations/alipay/validation/*.test.mjs

echo "[11/11] Machine payment showcase"
npm --prefix code/web-client/alipay-ai-pay-showcase test
npm --prefix code/web-client/alipay-ai-pay-showcase run build

echo "All repository checks passed."
