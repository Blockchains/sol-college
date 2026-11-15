import { MindsApiError, type BuilderMind, type MessageRecord, type WaitForReplyOutcome, type CircleMember } from "@animocabrands/minds-client-lib";
import type { MindsPort } from "../../src/minds/port.ts";

/** In-memory fake implementing the SDK-typed MindsPort (mock test double; not a live API). */
export class FakeMinds implements MindsPort {
  minds: BuilderMind[] = [{ mindId: "11111111-aaaa-bbbb-cccc-000000e7df11", name: "College", species: "moca", isEnabled: true, archetype: "chiefofstaff" }];
  awakenCalls = 0;
  sendCalls: string[] = [];
  history: MessageRecord[] = []; // newest-first
  awakenBehaviour: "ok" | "network-error" | "reject" = "ok";
  sendBehaviour: "ok" | "throw" = "ok";
  replyBehaviour: { kind: "timeout" } | { kind: "reply"; text: (sent: string) => string } = { kind: "timeout" };
  equipped: { skills: string[]; apps: string[] } = { skills: [], apps: [] };
  equipDrop: string[] = [];
  circle: CircleMember[] = [{ email: "steward@example.org", isSteward: true }];

  bazaar = {
    listSkills: async () => ({ totalCount: 0, page: 1, pageSize: 10, items: [] }),
    getSkill: async (skillId: string) => ({ skillId, name: "x" }),
    listApps: async () => ({ totalCount: 0, page: 1, pageSize: 10, items: [] }),
    getApp: async (appId: string) => ({ appId, appName: "x" }),
  };

  async listMinds() { return this.minds; }
  async getMind(mindId: string) { const m = this.minds.find((x) => x.mindId === mindId); if (!m) throw new MindsApiError({ status: 404, code: "not_found", message: "no" }); return { ...m, walletAddress: "0xabc", chain: "base", email: "x@hellominds.ai" }; }
  async checkMindName(name: string) { return { isAvailable: !this.minds.some((m) => m.name === name) }; }
  async awakenMind(o: { name: string; id: string }) {
    this.awakenCalls++;
    if (this.awakenBehaviour === "reject") throw new MindsApiError({ status: 400, code: "bad_archetype", message: "unknown archetype" });
    const m: BuilderMind = { mindId: `mind-${this.awakenCalls}-${o.name}`, name: o.name };
    this.minds.push(m);
    if (this.awakenBehaviour === "network-error") throw new Error("socket hang up");
    return m;
  }
  async updateMindStatus(mindId: string, b: { isEnabled: boolean }) { const m = this.minds.find((x) => x.mindId === mindId)!; m.isEnabled = b.isEnabled; return { msg: null, result: "ok" }; }
  async getCognitionBalance(mindId: string) { return { mindId, cognition: 583.44 }; }
  async getCognitionUsage() { return { items: [{ bucket: "2026-11-15T00:00:00", value: 1.62 }] }; }
  async getCognitionUsageByTool() { return { summary: [{ tool: "LLM_Turn", callCount: 4, creditsUsed: 1.62 }], timeline: [] }; }
  async listEquippedSkills() { return this.equipped.skills.map((skillId) => ({ skillId })); }
  async listEquippedApps() { return this.equipped.apps.map((appId) => ({ appId })); }
  async equipSkills(_m: string, b: { ids: string[] }) { const ok = b.ids.filter((i) => !this.equipDrop.includes(i)); this.equipped.skills.push(...ok); return { results: b.ids.map((skillId) => ({ skillId, isEquipped: ok.includes(skillId), changed: ok.includes(skillId) })) }; }
  async unequipSkills(_m: string, b: { ids: string[] }) { this.equipped.skills = this.equipped.skills.filter((s) => !b.ids.includes(s)); return { results: b.ids.map((skillId) => ({ skillId, isEquipped: false })) }; }
  async equipApps(_m: string, b: { ids: string[] }) { const ok = b.ids.filter((i) => !this.equipDrop.includes(i)); this.equipped.apps.push(...ok); return { results: b.ids.map((appId) => ({ appId, isEquipped: ok.includes(appId) })) }; }
  async unequipApps(_m: string, b: { ids: string[] }) { this.equipped.apps = this.equipped.apps.filter((s) => !b.ids.includes(s)); return { results: [] }; }
  async getCircle() { return this.circle; }
  async addCircleMembers(_m: string, b: { emails: string[] }) { for (const e of b.emails) this.circle.push({ email: e }); return { items: b.emails.map((email) => ({ email, action: "added" })), summary: {} }; }
  async removeCircleMembers(_m: string, b: { emails: string[] }) { this.circle = this.circle.filter((c) => !b.emails.includes(c.email ?? "")); return { items: b.emails.map((email) => ({ email, action: "removed" })), summary: {} }; }
  async ensureConversation(alias: string, mindId: string) { return { conversationId: `c-${alias}`, alias, mindId }; }
  async getConversation(alias: string) { return { conversationId: `c-${alias}`, alias }; }
  async listConversations() { return []; }
  async sendMessage(b: { alias: string; messageText: string }) {
    this.sendCalls.push(b.messageText);
    if (this.sendBehaviour === "throw") throw new Error("ECONNRESET");
    this.history.unshift({ fingerprint: `h${this.history.length + 1}`, senderType: 1, messageText: b.messageText });
    return {};
  }
  async getHistory() { return this.history; }
  async getLatestHistoryFingerprint() { return this.history[0]?.fingerprint; }
  async waitForReply(o: { sentMessageText?: string }): Promise<WaitForReplyOutcome> {
    await new Promise((r) => setTimeout(r, 5));
    if (this.replyBehaviour.kind === "timeout") return { timedOut: true };
    const reply: MessageRecord = { fingerprint: `h${this.history.length + 1}`, senderType: 0, messageText: this.replyBehaviour.text(o.sentMessageText ?? "") };
    this.history.unshift(reply);
    return { reply, timedOut: false };
  }
}

export function validReplyFor(taskId: string, project: string, extra: Record<string, unknown> = {}): string {
  return "Here you go\n```json\n" + JSON.stringify({ protocol: "sc-task-response/1", taskId, project, summary: "ok", facts: [{ statement: "take_and_close previously aborted", sourceRefs: ["s1"] }], hypotheses: [{ statement: "h", howToTest: "run fixture" }], proposals: [], evidenceRefs: [], uncertainties: [], ...extra }) + "\n```";
}
