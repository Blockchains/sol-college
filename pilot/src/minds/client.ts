import { BUILDER_API_KEY_ENV, createMindsClient } from "@animocabrands/minds-client-lib";
import type { MindsPort } from "./port.ts";

/**
 * Server-side (trusted runtime) client. Reads the Builder key from the environment only; the SDK
 * does not load .env. Never call this from browser code or from a job that executes contributor code.
 */
export function createServerMindsClient(env: NodeJS.ProcessEnv = process.env): MindsPort {
  const builderApiKey = env[BUILDER_API_KEY_ENV];
  if (!builderApiKey) throw new Error(`${BUILDER_API_KEY_ENV} is not set`);
  return createMindsClient({ builderApiKey });
}

/** Public catalogue only (no credential). */
export function createPublicCatalogueClient(): MindsPort["bazaar"] {
  return createMindsClient({}).bazaar;
}

export function builderKeyFromEnv(env: NodeJS.ProcessEnv = process.env): string | undefined {
  return env[BUILDER_API_KEY_ENV];
}
