import {
  generateKeyPairSync,
  sign as nodeSign,
  verify as nodeVerify,
} from "node:crypto";

import { canonicalize } from "./canonical.ts";
import type {
  Ed25519KeyPair,
  PublicKeyReference,
  SignatureProof,
} from "./types.ts";

export type KeyMaterial = string | Uint8Array;

function randomKeyId(): string {
  return `key-${crypto.randomUUID()}`;
}

function keyValue(key: PublicKeyReference | KeyMaterial): KeyMaterial {
  if (typeof key === "object" && !(key instanceof Uint8Array)) {
    return key.value;
  }
  return key;
}

export function generateEd25519KeyPair(keyId = randomKeyId()): Ed25519KeyPair {
  const pair = generateKeyPairSync("ed25519");
  const publicKey = pair.publicKey.export({ type: "spki", format: "pem" }).toString();
  const privateKey = pair.privateKey.export({ type: "pkcs8", format: "pem" }).toString();

  return {
    algorithm: "Ed25519",
    keyId,
    publicKey: {
      keyId,
      format: "pem-spki",
      value: publicKey,
    },
    privateKey,
  };
}

export function signCanonical(
  value: unknown,
  privateKey: KeyMaterial,
  keyId?: string,
): SignatureProof {
  const payload = Buffer.from(canonicalize(value), "utf8");
  const signatureValue = nodeSign(null, payload, privateKey).toString("base64url");
  return {
    signatureAlgorithm: "Ed25519",
    signatureValue,
    ...(keyId === undefined ? {} : { keyId }),
  };
}

export function verifyCanonicalSignature(
  value: unknown,
  proof: SignatureProof | string,
  publicKey: PublicKeyReference | KeyMaterial,
): boolean {
  const signatureAlgorithm =
    typeof proof === "string" ? "Ed25519" : proof.signatureAlgorithm;
  if (signatureAlgorithm !== "Ed25519") return false;

  try {
    const payload = Buffer.from(canonicalize(value), "utf8");
    const signatureValue =
      typeof proof === "string" ? proof : proof.signatureValue;
    return nodeVerify(
      null,
      payload,
      keyValue(publicKey),
      Buffer.from(signatureValue, "base64url"),
    );
  } catch {
    return false;
  }
}

export const generateKeyPair = generateEd25519KeyPair;
export const sign = signCanonical;
export const verify = verifyCanonicalSignature;
