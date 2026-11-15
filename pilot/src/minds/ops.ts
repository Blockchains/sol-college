import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import type { MindsPort } from "./port.ts";
import { shortRef } from "../lib/secrets.ts";

export function installedSdkVersion(): string {
  const require = createRequire(import.meta.url);
  const pkgPath = require.resolve("@animocabrands/minds-client-lib").replace(/dist\/index\.js$/, "package.json");
  return (JSON.parse(readFileSync(pkgPath, "utf8")) as { version: string }).version;
}

/** Account inventory without exposing private identifiers (mind IDs shortened, no emails/wallets). */
export async function inventory(minds: Pick<MindsPort, "listMinds" | "listConversations">) {
  const list = await minds.listMinds();
  const convs = await minds.listConversations();
  return {
    mindCount: list.length,
    minds: list.map((m) => ({ ref: shortRef(m.mindId), name: m.name ?? null, species: m.species ?? null, isEnabled: m.isEnabled ?? null })),
    conversationAliases: convs.map((c) => c.alias ?? null),
  };
}

export async function telemetry(minds: Pick<MindsPort, "getCognitionBalance" | "getCognitionUsage" | "getCognitionUsageByTool">, mindId: string) {
  const balance = await minds.getCognitionBalance(mindId);
  const usage = await minds.getCognitionUsage(mindId, { interval: "1d" });
  const byTool = await minds.getCognitionUsageByTool(mindId, { interval: "day" });
  return {
    cognitionBalance: balance.cognition,
    usageDaily: usage.items.map((i) => ({ bucket: i.bucket, value: i.value })),
    byTool: byTool.summary.map((s) => ({ tool: s.tool, callCount: s.callCount, creditsUsed: s.creditsUsed })),
  };
}

export async function capabilities(minds: Pick<MindsPort, "listEquippedSkills" | "listEquippedApps" | "getCircle">, mindId: string) {
  const skills = await minds.listEquippedSkills(mindId);
  const apps = await minds.listEquippedApps(mindId);
  const circle = await minds.getCircle(mindId);
  return {
    skills: skills.map((s) => ({ skillId: s.skillId, name: s.name ?? null, source: s.source ?? null })),
    apps: apps.map((a) => ({ appId: a.appId, appName: a.appName ?? null, tier: a.tier ?? null, version: a.version ?? null })),
    circle: { memberCount: circle.length, stewards: circle.filter((m) => m.isSteward).length, minds: circle.filter((m) => (m.email ?? "").endsWith("@hellominds.ai")).length },
  };
}

export async function mindDetail(minds: Pick<MindsPort, "getMind">, mindId: string) {
  const m = await minds.getMind(mindId);
  return {
    ref: shortRef(m.mindId),
    name: m.name ?? null,
    archetype: typeof m["archetype"] === "string" ? (m["archetype"] as string) : null,
    species: m.species ?? null,
    isEnabled: m.isEnabled ?? null,
    hasWallet: Boolean(m.walletAddress),
    chain: m.chain ?? null,
    walletNote: "walletAddress/chain alone do not establish Solana signing, recurring debit or payment settlement",
  };
}
