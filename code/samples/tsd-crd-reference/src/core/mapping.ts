import { canonicalize } from "./canonical.ts";
import type { JsonValue, MappingPolicyReference, MappingTrace } from "./types.ts";

export interface CreateMappingTraceInput {
  subjectCreditAssertionRef: string;
  associatedCreditValue: JsonValue;
  mappingPolicy: MappingPolicyReference;
}

function nonBlank(value: string): boolean {
  return typeof value === "string" && value.trim().length > 0;
}

export function createMappingTrace(input: CreateMappingTraceInput): MappingTrace {
  const trace: MappingTrace = {
    subjectCreditAssertionRef: input.subjectCreditAssertionRef,
    associatedCreditValue: structuredClone(input.associatedCreditValue),
    mappingPolicy: structuredClone(input.mappingPolicy),
    creditSource: "ASSOCIATED_CREDIT",
  };
  const result = validateMappingTrace(trace);
  if (!result.valid) throw new TypeError(result.errors.join("; "));
  return trace;
}

export interface MappingValidationResult {
  valid: boolean;
  errors: string[];
}

export function validateMappingTrace(trace: MappingTrace): MappingValidationResult {
  const errors: string[] = [];
  if (!nonBlank(trace.subjectCreditAssertionRef)) {
    errors.push("subjectCreditAssertionRef is required");
  }
  if (!nonBlank(trace.mappingPolicy?.id)) errors.push("mappingPolicy.id is required");
  if (!nonBlank(trace.mappingPolicy?.version)) {
    errors.push("mappingPolicy.version is required");
  }
  if (trace.creditSource !== "ASSOCIATED_CREDIT") {
    errors.push("creditSource must be ASSOCIATED_CREDIT");
  }
  if (trace.associatedCreditValue === null) {
    errors.push("associatedCreditValue must not be null");
  } else if (
    typeof trace.associatedCreditValue === "string"
    && trace.associatedCreditValue.length === 0
  ) {
    errors.push("associatedCreditValue must not be empty");
  } else if (
    Array.isArray(trace.associatedCreditValue)
    && trace.associatedCreditValue.length === 0
  ) {
    errors.push("associatedCreditValue must not be an empty array");
  } else if (
    typeof trace.associatedCreditValue === "object"
    && !Array.isArray(trace.associatedCreditValue)
    && Object.keys(trace.associatedCreditValue).length === 0
  ) {
    errors.push("associatedCreditValue must not be an empty object");
  }
  try {
    canonicalize(trace.associatedCreditValue);
  } catch (error) {
    errors.push(error instanceof Error ? error.message : "associatedCreditValue is invalid");
  }
  return { valid: errors.length === 0, errors };
}

export function mappingTraceFromCredential(input: {
  subjectCreditAssertionRef?: string;
  associatedCreditValue: JsonValue;
  mappingPolicy: MappingPolicyReference;
  creditSource: "ASSOCIATED_CREDIT";
}): MappingTrace | undefined {
  if (input.subjectCreditAssertionRef === undefined) return undefined;
  return {
    subjectCreditAssertionRef: input.subjectCreditAssertionRef,
    associatedCreditValue: structuredClone(input.associatedCreditValue),
    mappingPolicy: structuredClone(input.mappingPolicy),
    creditSource: input.creditSource,
  };
}
