#!/usr/bin/env python3
"""Dependency-free drift and fixture checks for A402 implementation artifacts."""

from __future__ import annotations

import base64
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "code/schemas/a402"
FIXTURE_DIR = SCHEMA_DIR / "fixtures"
ASSERTION_DIR = SCHEMA_DIR / "tests"

SCHEMAS = {
    "payment-needed.schema.json",
    "payment-proof.schema.json",
    "payment-validation.schema.json",
    "error.schema.json",
    "transaction-state.schema.json",
    "workflow-binding-manifest.schema.json",
    "common.schema.json",
}

VALID_FIXTURES = {
    "payment-needed.json": "payment-needed.schema.json",
    "payment-proof.json": "payment-proof.schema.json",
    "payment-validation.json": "payment-validation.schema.json",
    "error.json": "error.schema.json",
    "workflow-binding-manifest.json": "workflow-binding-manifest.schema.json",
}

INVALID_FIXTURES = {
    "payment-needed-missing-method-id.json": "payment-needed.schema.json",
    "payment-proof-padding-and-no-idempotency.json": "payment-proof.schema.json",
    "payment-validation-collapsed-success.json": "payment-validation.schema.json",
}

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

ALLOWED_TRANSITIONS = {
    ("CREATE", "PAYMENT_NEEDED_ISSUED", "WAIT_BUYER_PAY"),
    ("WAIT_BUYER_PAY", "PAYMENT_VALIDATED", "WAIT_SELLER_FULFILLMENT"),
    ("WAIT_BUYER_PAY", "PAYMENT_TERMINATED", "TRADE_CLOSED"),
    ("WAIT_SELLER_FULFILLMENT", "DELIVERY_COMMITTED", "WAIT_BUYER_RECEIPT"),
    ("WAIT_SELLER_FULFILLMENT", "COMPENSATION_COMPLETED", "TRADE_CLOSED"),
    ("WAIT_BUYER_RECEIPT", "FULFILLMENT_CONFIRMED", "TRADE_FINISHED"),
    ("WAIT_BUYER_RECEIPT", "TRADE_TERMINATED", "TRADE_CLOSED"),
}

ERROR_CATEGORIES = {
    "SIGNATURE_VALIDATION",
    "REQUEST_PARAMETER",
    "PROTOCOL_METHOD",
    "PARTICIPANT_IDENTITY",
    "LIMIT_ASSET",
    "AUTHORIZATION_RISK",
    "TRANSACTION_STATE",
    "REFUND",
    "FULFILLMENT_RECEIPT",
    "PAYMENT_PROOF_VALIDATION",
    "SYSTEM",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def json_pointer(document, pointer: str):
    value = document
    if not pointer:
        return value
    if not pointer.startswith("/"):
        raise ValueError(f"unsupported JSON pointer: {pointer}")
    for raw_part in pointer[1:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def type_matches(value, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    raise ValueError(f"unsupported JSON Schema type: {expected}")


def format_matches(value: str, name: str) -> bool:
    if name == "date-time":
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return "T" in value and (value.endswith("Z") or "+" in value[10:])
        except ValueError:
            return False
    if name == "uri":
        parsed = urlsplit(value)
        return bool(parsed.scheme and parsed.netloc and not parsed.fragment)
    raise ValueError(f"unsupported JSON Schema format: {name}")


def validate(instance, schema, document_path: Path, at: str = "$") -> list[str]:
    errors: list[str] = []

    if "$ref" in schema:
        ref_document, _, fragment = schema["$ref"].partition("#")
        target_path = document_path if not ref_document else document_path.parent / ref_document
        target_document = load_json(target_path)
        return validate(instance, json_pointer(target_document, fragment), target_path, at)

    expected_type = schema.get("type")
    if expected_type is not None:
        options = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(type_matches(instance, option) for option in options):
            return [f"{at}: expected type {expected_type!r}, got {type(instance).__name__}"]

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{at}: expected constant {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{at}: value {instance!r} is not in the allowed enum")

    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{at}: string is shorter than minLength")
        if len(instance) > schema.get("maxLength", sys.maxsize):
            errors.append(f"{at}: string is longer than maxLength")
        if "pattern" in schema and re.fullmatch(schema["pattern"], instance) is None:
            errors.append(f"{at}: string does not match {schema['pattern']!r}")
        if "format" in schema and not format_matches(instance, schema["format"]):
            errors.append(f"{at}: string is not a valid {schema['format']}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if instance < schema.get("minimum", float("-inf")):
            errors.append(f"{at}: value is below minimum")
        if instance > schema.get("maximum", float("inf")):
            errors.append(f"{at}: value is above maximum")

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for name in required:
            if name not in instance:
                errors.append(f"{at}: missing required property {name!r}")
        if len(instance) < schema.get("minProperties", 0):
            errors.append(f"{at}: object has fewer than minProperties")
        properties = schema.get("properties", {})
        for name, value in instance.items():
            if name in properties:
                errors.extend(validate(value, properties[name], document_path, f"{at}.{name}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{at}: unexpected property {name!r}")

    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"{at}: array has fewer than minItems")
        if len(instance) > schema.get("maxItems", sys.maxsize):
            errors.append(f"{at}: array has more than maxItems")
        if schema.get("uniqueItems"):
            canonical = [json.dumps(item, sort_keys=True, separators=(",", ":")) for item in instance]
            if len(canonical) != len(set(canonical)):
                errors.append(f"{at}: array items are not unique")
        if "items" in schema:
            for index, value in enumerate(instance):
                errors.extend(validate(value, schema["items"], document_path, f"{at}[{index}]"))

    return errors


def semantic_payload_errors(payload: dict, kind: str) -> list[str]:
    # ACT 2.1 invariant: validation, delivery and fulfillment stay distinct outcomes.
    errors: list[str] = []
    protocol = payload.get("protocol", {})
    method = protocol.get("request_method")
    if kind in {"payment-needed", "payment-proof"} and method not in SAFE_METHODS:
        if not protocol.get("idempotency_key"):
            errors.append(f"{kind}: non-idempotent request needs idempotency_key")
    if kind == "payment-validation":
        status = protocol.get("validation_status")
        if status == "VALID" and "error" in protocol:
            errors.append("payment-validation: VALID must not carry error")
        if status in {"INVALID", "UNKNOWN"} and "error" not in protocol:
            errors.append("payment-validation: INVALID/UNKNOWN must carry error")
        if "delivery_status" not in protocol or "fulfillment_status" not in protocol:
            errors.append("payment-validation: phase outcomes must remain separately observable")
    return errors


def check_schema_set() -> list[str]:
    errors: list[str] = []
    actual = {path.name for path in SCHEMA_DIR.glob("*.schema.json")}
    if actual != SCHEMAS:
        errors.append(f"schema file set drift: expected {sorted(SCHEMAS)}, found {sorted(actual)}")
    ids: set[str] = set()
    for name in sorted(SCHEMAS):
        path = SCHEMA_DIR / name
        schema = load_json(path)
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"{name}: must use JSON Schema Draft 2020-12")
        schema_id = schema.get("$id")
        if not schema_id or schema_id in ids:
            errors.append(f"{name}: missing or duplicate $id")
        ids.add(schema_id)
        if "Implementation Artifact / Non-normative" not in schema.get("$comment", ""):
            errors.append(f"{name}: missing Implementation Artifact / Non-normative marker")
    return errors


def check_assertion_catalog() -> list[str]:
    errors: list[str] = []
    schema_path = ASSERTION_DIR / "assertion-catalog.schema.json"
    catalog_path = ASSERTION_DIR / "a402-assertions.json"
    schema = load_json(schema_path)
    catalog = load_json(catalog_path)
    errors.extend(
        f"tests/a402-assertions.json: {error}"
        for error in validate(catalog, schema, schema_path)
    )

    assertions = catalog.get("assertions", [])
    expected_ids = {
        *(f"A402-TEST-{number:03d}" for number in range(1, 9)),
        *(f"PSD-TEST-{number:03d}" for number in range(1, 6)),
    }
    actual_ids = [assertion.get("id") for assertion in assertions if isinstance(assertion, dict)]
    if set(actual_ids) != expected_ids or len(actual_ids) != len(expected_ids):
        errors.append("tests/a402-assertions.json: stable assertion ID set drift")

    for assertion in assertions:
        if not isinstance(assertion, dict):
            continue
        assertion_id = assertion.get("id", "unknown")
        source = assertion.get("source")
        if isinstance(source, str):
            source_path = (ASSERTION_DIR / source.split("#", 1)[0]).resolve()
            if not source_path.is_file():
                errors.append(f"{assertion_id}: specification source does not exist")
        executable = assertion.get("executable_check")
        if isinstance(executable, str):
            executable_path = ROOT / executable.split("#", 1)[0]
            if not executable_path.is_file():
                errors.append(f"{assertion_id}: executable check target does not exist")
    return errors


def check_fixtures() -> list[str]:
    # ACT 2.1 invariants: proof validation and original-request correlation.
    errors: list[str] = []
    valid_dir = FIXTURE_DIR / "valid"
    invalid_dir = FIXTURE_DIR / "invalid"
    actual_valid = {path.name for path in valid_dir.glob("*.json")}
    actual_invalid = {path.name for path in invalid_dir.glob("*.json")}
    if actual_valid != set(VALID_FIXTURES):
        errors.append(f"valid fixture set drift: {sorted(actual_valid)}")
    if actual_invalid != set(INVALID_FIXTURES):
        errors.append(f"invalid fixture set drift: {sorted(actual_invalid)}")

    valid_payloads = {}
    for fixture_name, schema_name in VALID_FIXTURES.items():
        payload = load_json(valid_dir / fixture_name)
        fixture_errors = validate(payload, load_json(SCHEMA_DIR / schema_name), SCHEMA_DIR / schema_name)
        kind = fixture_name.removesuffix(".json")
        fixture_errors.extend(semantic_payload_errors(payload, kind))
        errors.extend(f"valid/{fixture_name}: {error}" for error in fixture_errors)
        valid_payloads[fixture_name] = payload

    for fixture_name, schema_name in INVALID_FIXTURES.items():
        payload = load_json(invalid_dir / fixture_name)
        kind = fixture_name.split("-missing", 1)[0].split("-padding", 1)[0].split("-collapsed", 1)[0]
        fixture_errors = validate(payload, load_json(SCHEMA_DIR / schema_name), SCHEMA_DIR / schema_name)
        fixture_errors.extend(semantic_payload_errors(payload, kind))
        if not fixture_errors:
            errors.append(f"invalid/{fixture_name}: unexpectedly passed")

    for fixture_name in ("payment-needed.json", "payment-proof.json", "payment-validation.json"):
        raw = json.dumps(valid_payloads[fixture_name], sort_keys=True, separators=(",", ":")).encode()
        encoded = base64.urlsafe_b64encode(raw).decode().rstrip("=")
        if "=" in encoded or re.fullmatch(r"[A-Za-z0-9_-]+", encoded) is None:
            errors.append(f"valid/{fixture_name}: non-canonical Base64URL encoding")
        decoded = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        if decoded != raw:
            errors.append(f"valid/{fixture_name}: Base64URL round-trip failed")

    needed = valid_payloads["payment-needed.json"]["protocol"]
    proof = valid_payloads["payment-proof.json"]["protocol"]
    validation = valid_payloads["payment-validation.json"]["protocol"]
    for field in ("method_id", "method_version", "out_trade_no", "resource_id", "request_fingerprint"):
        if len({needed[field], proof[field], validation[field]}) != 1:
            errors.append(f"flow fixture correlation drift for {field}")
    for field in ("request_method", "idempotency_key"):
        if needed[field] != proof[field]:
            errors.append(f"flow fixture retry drift for {field}")
    if proof["trade_no"] != validation["trade_no"]:
        errors.append("flow fixture trade_no drift")
    return errors


def check_errors_and_states() -> list[str]:
    # ACT 2.1 invariant: failures retain phase, retryability and valid next actions.
    errors: list[str] = []
    error_schema_path = SCHEMA_DIR / "error.schema.json"
    error_schema = load_json(error_schema_path)
    catalog = load_json(SCHEMA_DIR / "error-catalog.json")
    if catalog.get("status") != "implementation-artifact" or catalog.get("normative") is not False:
        errors.append("error-catalog.json: must remain an implementation artifact and non-normative")
    entries = catalog.get("errors", [])
    categories = [entry.get("category") for entry in entries]
    ids = [entry.get("error_id") for entry in entries]
    if set(categories) != ERROR_CATEGORIES or len(categories) != len(ERROR_CATEGORIES):
        errors.append("error-catalog.json: must cover each of the eleven source categories exactly once")
    if len(ids) != len(set(ids)):
        errors.append("error-catalog.json: duplicate error_id")
    for index, entry in enumerate(entries):
        errors.extend(
            f"error-catalog.json.errors[{index}]: {error}"
            for error in validate(entry, error_schema, error_schema_path)
        )

    state_path = SCHEMA_DIR / "transaction-state.schema.json"
    state_schema = load_json(state_path)
    transitions = load_json(FIXTURE_DIR / "state-transitions.json")
    allowed = {(item["from"], item["event"], item["to"]) for item in transitions.get("allowed", [])}
    forbidden = {(item["from"], item["event"], item["to"]) for item in transitions.get("forbidden", [])}
    if allowed != ALLOWED_TRANSITIONS:
        errors.append("state-transitions.json: allowed transition set drift")
    if allowed & forbidden:
        errors.append("state-transitions.json: transition cannot be both allowed and forbidden")
    for group in ("allowed", "forbidden"):
        for index, transition in enumerate(transitions.get(group, [])):
            errors.extend(
                f"state-transitions.json.{group}[{index}]: {error}"
                for error in validate(transition, state_schema, state_path)
            )
    if any(source in {"TRADE_FINISHED", "TRADE_CLOSED"} for source, _, _ in allowed):
        errors.append("state-transitions.json: terminal states must not have outgoing transitions")
    return errors


def main() -> int:
    errors = (
        check_schema_set()
        + check_assertion_catalog()
        + check_fixtures()
        + check_errors_and_states()
    )
    if errors:
        print("A402 implementation artifact validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        "A402 implementation artifacts passed: 7 schemas, 13 assertions, "
        "5 valid fixtures, 3 invalid fixtures, 11 errors, 7 state transitions, "
        "and Base64URL round-trips."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
