import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import type { MindsPort } from "./port.ts";
import { shortRef } from "../lib/secrets.ts";

export function installedSdkVersion(): string {
  const entry = fileURLToPath(import.meta.resolve("@animocabrands/minds-client-lib"));
  const pkgPath = entry.replace(/dist\/index\.js$/, "package.json");
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

/**
 * Public, sanitised operations snapshot for one project Mind: every read the SDK offers that is meaningful on the
 * campus ops view (status, cognition balance, daily usage, usage by tool, equipped skills and apps, this project's
 * conversation count). No Mind IDs, emails, wallet addresses or message text.
 */
export async function opsSnapshot(minds: Pick<MindsPort, "getMind" | "getCognitionBalance" | "getCognitionUsage" | "getCognitionUsageByTool" | "listEquippedSkills" | "listEquippedApps" | "listConversations">, mindId: string, aliasPrefix: string) {
  const m = await minds.getMind(mindId);
  const [t, skills, apps, convs] = await Promise.all([
    telemetry(minds, mindId),
    minds.listEquippedSkills(mindId),
    minds.listEquippedApps(mindId),
    minds.listConversations(),
  ]);
  return {
    isEnabled: m.isEnabled ?? null,
    cognitionBalance: t.cognitionBalance,
    usageDaily: t.usageDaily.slice(-14),
    usageByTool: t.byTool,
    skills: skills.map((s) => ({ name: s.name ?? null, source: s.source ?? null })),
    apps: apps.map((a) => ({ name: a.appName ?? null, tier: a.tier ?? null })),
    conversations: convs.filter((c) => (c.alias ?? "").startsWith(`${aliasPrefix}-`)).length,
    sdkVersion: installedSdkVersion(),
  };
}
