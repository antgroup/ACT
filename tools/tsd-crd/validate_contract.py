#!/usr/bin/env python3
"""Dependency-free integrity checks for non-normative TSD-CRD artifacts."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[2]
PROFILE_DIR = ROOT / "code/schemas/tsd-crd/reference-v1"
SCHEMA_DIR = PROFILE_DIR / "schemas"
EXAMPLE_DIR = PROFILE_DIR / "examples"
VECTOR_DIR = PROFILE_DIR / "test-vectors"
OPENAPI_PATH = PROFILE_DIR / "openapi/openapi.yaml"

SCHEMAS = {
    "agent-associated-credit-assertion.schema.json",
    "association-application.schema.json",
    "association-credential.schema.json",
    "authorization-revocation-request.schema.json",
    "common.schema.json",
    "credential-status.schema.json",
    "credit-query-authorization.schema.json",
    "direct-signing-payload.schema.json",
    "status-change-request.schema.json",
    "subject-credit-assertion.schema.json",
    "verification-request.schema.json",
    "verification-response.schema.json",
}

EXAMPLES = {
    "agent-associated-credit-assertion.json": "agent-associated-credit-assertion.schema.json",
    "association-application-attested.json": "association-application.schema.json",
    "association-application-direct.json": "association-application.schema.json",
    "association-credential-attested.json": "association-credential.schema.json",
    "association-credential-direct.json": "association-credential.schema.json",
    "credential-status-active.json": "credential-status.schema.json",
    "credit-query-authorization-per-request.json": "credit-query-authorization.schema.json",
    "credit-query-authorization-platform-delegated.json": "credit-query-authorization.schema.json",
    "status-change-suspend.json": "status-change-request.schema.json",
    "subject-credit-assertion.json": "subject-credit-assertion.schema.json",
    "verification-request-associated-credit.json": "verification-request.schema.json",
    "verification-request-credential.json": "verification-request.schema.json",
    "verification-response-associated-credit-pass.json": "verification-response.schema.json",
    "verification-response-credential-pass.json": "verification-response.schema.json",
    "verification-response-inconclusive.json": "verification-response.schema.json",
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
        return bool(parsed.scheme and not any(character.isspace() for character in value))
    if name == "uri-reference":
        return bool(value) and not any(character.isspace() for character in value)
    raise ValueError(f"unsupported JSON Schema format: {name}")


def validate(instance, schema, document_path: Path, at: str = "$") -> list[str]:
    if schema is True:
        return []
    if schema is False:
        return [f"{at}: false schema rejects the value"]

    errors: list[str] = []
    if "$ref" in schema:
        ref_document, _, fragment = schema["$ref"].partition("#")
        target_path = document_path if not ref_document else (document_path.parent / ref_document).resolve()
        target_document = load_json(target_path)
        errors.extend(validate(instance, json_pointer(target_document, fragment), target_path, at))

    for subschema in schema.get("allOf", []):
        errors.extend(validate(instance, subschema, document_path, at))

    if "anyOf" in schema:
        branches = [validate(instance, item, document_path, at) for item in schema["anyOf"]]
        if all(branch for branch in branches):
            errors.append(f"{at}: value does not match any anyOf branch")

    if "oneOf" in schema:
        matches = sum(not validate(instance, item, document_path, at) for item in schema["oneOf"])
        if matches != 1:
            errors.append(f"{at}: value matches {matches} oneOf branches, expected exactly one")

    if "not" in schema and not validate(instance, schema["not"], document_path, at):
        errors.append(f"{at}: value matches a forbidden schema")

    if "if" in schema:
        branch = "then" if not validate(instance, schema["if"], document_path, at) else "else"
        if branch in schema:
            errors.extend(validate(instance, schema[branch], document_path, at))

    expected_type = schema.get("type")
    if expected_type is not None:
        options = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(type_matches(instance, option) for option in options):
            return errors + [f"{at}: expected type {expected_type!r}, got {type(instance).__name__}"]

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{at}: expected constant {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{at}: value {instance!r} is not in the allowed enum")

    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{at}: string is shorter than minLength")
        if len(instance) > schema.get("maxLength", sys.maxsize):
            errors.append(f"{at}: string is longer than maxLength")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append(f"{at}: string does not match {schema['pattern']!r}")
        if "format" in schema and not format_matches(instance, schema["format"]):
            errors.append(f"{at}: string is not a valid {schema['format']}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if instance < schema.get("minimum", float("-inf")):
            errors.append(f"{at}: value is below minimum")
        if instance > schema.get("maximum", float("inf")):
            errors.append(f"{at}: value is above maximum")

    if isinstance(instance, dict):
        for name in schema.get("required", []):
            if name not in instance:
                errors.append(f"{at}: missing required property {name!r}")
        if len(instance) < schema.get("minProperties", 0):
            errors.append(f"{at}: object has fewer than minProperties")
        if len(instance) > schema.get("maxProperties", sys.maxsize):
            errors.append(f"{at}: object has more than maxProperties")
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


def check_schema_set() -> list[str]:
    errors: list[str] = []
    actual = {path.name for path in SCHEMA_DIR.glob("*.schema.json")}
    if actual != SCHEMAS:
        errors.append(f"schema file set drift: expected {sorted(SCHEMAS)}, found {sorted(actual)}")
    identifiers: set[str] = set()
    for name in sorted(SCHEMAS):
        path = SCHEMA_DIR / name
        schema = load_json(path)
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"{name}: must use JSON Schema Draft 2020-12")
        identifier = schema.get("$id")
        if identifier != name or identifier in identifiers:
            errors.append(f"{name}: $id must be the unique relative schema filename")
        identifiers.add(identifier)
        if "Implementation Artifact / Non-normative" not in schema.get("$comment", ""):
            errors.append(f"{name}: missing non-normative marker")
    return errors


def check_examples() -> list[str]:
    errors: list[str] = []
    actual = {path.name for path in EXAMPLE_DIR.glob("*.json")}
    if actual != set(EXAMPLES):
        errors.append(f"example file set drift: expected {sorted(EXAMPLES)}, found {sorted(actual)}")
    for example_name, schema_name in EXAMPLES.items():
        example_path = EXAMPLE_DIR / example_name
        schema_path = SCHEMA_DIR / schema_name
        for error in validate(load_json(example_path), load_json(schema_path), schema_path):
            errors.append(f"examples/{example_name}: {error}")
    return errors


def check_openapi_references() -> list[str]:
    errors: list[str] = []
    text = OPENAPI_PATH.read_text(encoding="utf-8")
    if not text.startswith("openapi: 3.1.0\n"):
        errors.append("openapi/openapi.yaml: must declare OpenAPI 3.1.0")
    if "Non-normative local Sandbox binding" not in text:
        errors.append("openapi/openapi.yaml: missing non-normative marker")
    references = re.findall(r"(?:\$ref|externalValue):\s*[\"']?([^\s\"']+)", text)
    for reference in references:
        if reference.startswith("#"):
            continue
        target = reference.split("#", 1)[0]
        if not (OPENAPI_PATH.parent / target).resolve().is_file():
            errors.append(f"openapi/openapi.yaml: unresolved local reference {reference}")
    return errors


def check_vectors() -> list[str]:
    errors: list[str] = []
    counts = {}
    for kind in ("valid", "invalid"):
        paths = sorted((VECTOR_DIR / kind).glob("*.json"))
        counts[kind] = len(paths)
        if not paths:
            errors.append(f"test-vectors/{kind}: no vectors found")
        for path in paths:
            value = load_json(path)
            if not isinstance(value, dict):
                errors.append(f"test-vectors/{kind}/{path.name}: vector must be an object")
                continue
            if "expectedValid" in value and value["expectedValid"] is not (kind == "valid"):
                errors.append(f"test-vectors/{kind}/{path.name}: expectedValid disagrees with directory")
    return errors


def main() -> int:
    errors = check_schema_set() + check_examples() + check_openapi_references() + check_vectors()
    if errors:
        print("TSD-CRD implementation artifact validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    valid_count = len(list((VECTOR_DIR / "valid").glob("*.json")))
    invalid_count = len(list((VECTOR_DIR / "invalid").glob("*.json")))
    print(
        f"TSD-CRD artifacts passed: {len(SCHEMAS)} schemas, {len(EXAMPLES)} examples, "
        f"OpenAPI references, {valid_count} valid vectors, and {invalid_count} invalid vectors."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
