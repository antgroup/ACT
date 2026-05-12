export interface DidDocument {
  '@context': string[];
  id: string;
  controller?: string;
  verificationMethod: {
    id: string;
    type: string;
    controller: string;
    publicKeyJwk: {
      kty: string;
      crv: string;
      x: string;
      y: string;
    };
  }[];
  authentication: string[];
  assertionMethod?: string[];
  service?: {
    id: string;
    type: string;
    serviceEndpoint: string;
  }[];
}

export class DidActResolver {
  async resolve(did: string): Promise<DidDocument> {
    const match = did.match(/^did:act:([^/]+)\/(.+)$/);
    if (!match) throw new Error(`Invalid did:act identifier: ${did}`);

    const domain = match[1];
    const identifier = match[2];
    const url = `https://${domain}/.well-known/did-act/${identifier}`;

    const response = await fetch(url);
    if (!response.ok) throw new Error(`Failed to resolve DID: ${did}`);

    return response.json() as Promise<DidDocument>;
  }
}