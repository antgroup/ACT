function assertWellFormedUnicode(value: string): void {
  for (let index = 0; index < value.length; index += 1) {
    const codeUnit = value.charCodeAt(index);
    if (codeUnit >= 0xd800 && codeUnit <= 0xdbff) {
      const next = value.charCodeAt(index + 1);
      if (!(next >= 0xdc00 && next <= 0xdfff)) {
        throw new TypeError("Canonical JSON rejects unpaired high surrogates");
      }
      index += 1;
      continue;
    }
    if (codeUnit >= 0xdc00 && codeUnit <= 0xdfff) {
      throw new TypeError("Canonical JSON rejects unpaired low surrogates");
    }
  }
}

function serialize(value: unknown, stack: Set<object>): string {
  if (value === null) return "null";

  if (typeof value === "string") {
    assertWellFormedUnicode(value);
    return JSON.stringify(value);
  }

  if (typeof value === "boolean") return value ? "true" : "false";

  if (typeof value === "number") {
    if (!Number.isFinite(value)) {
      throw new TypeError("Canonical JSON only supports finite numbers");
    }
    if (Object.is(value, -0)) {
      throw new TypeError("Canonical JSON rejects negative zero");
    }
    return JSON.stringify(value);
  }

  if (typeof value !== "object") {
    throw new TypeError(`Canonical JSON cannot serialize ${typeof value}`);
  }

  if (stack.has(value)) {
    throw new TypeError("Canonical JSON cannot serialize cyclic values");
  }
  stack.add(value);

  try {
    if (Array.isArray(value)) {
      const items: string[] = [];
      for (let index = 0; index < value.length; index += 1) {
        if (!Object.hasOwn(value, index)) {
          throw new TypeError("Canonical JSON rejects sparse arrays");
        }
        items.push(serialize(value[index], stack));
      }
      return `[${items.join(",")}]`;
    }

    const prototype = Object.getPrototypeOf(value);
    if (prototype !== Object.prototype && prototype !== null) {
      throw new TypeError("Canonical JSON only supports plain objects");
    }

    const record = value as Record<string, unknown>;
    const keys = Object.keys(record).sort();
    const members = keys.map((key) => {
      assertWellFormedUnicode(key);
      return `${JSON.stringify(key)}:${serialize(record[key], stack)}`;
    });
    return `{${members.join(",")}}`;
  } finally {
    stack.delete(value);
  }
}

/**
 * Produces deterministic JSON using RFC 8785-compatible ordering and number
 * rendering. Values outside the interoperable JSON data model are rejected.
 */
export function canonicalize(value: unknown): string {
  return serialize(value, new Set<object>());
}

export const canonicalJson = canonicalize;
