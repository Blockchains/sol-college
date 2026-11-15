/**
 * Operator CLI (trusted runtime only: the operator's machine or a protected GitHub environment job).
 *   minds inventory
 *   minds project <slug> | reconcile <slug> | telemetry <slug> | capabilities <slug>       (read-only)
 *   minds provision <slug> --name N --archetype A --approve REF --approved-by LOGIN        (mutation)
 *   minds equip <slug> --skills id,id | --apps id,id --approve REF --approved-by LOGIN    (mutation)
 *   minds circle <slug> --add e1,e2 --remove e3 --approve REF --approved-by LOGIN         (mutation)
 *   minds pause <slug> | resume <slug> --approve REF --approved-by LOGIN                  (mutation)
 *   minds smoke-test --mind-name NAME [--allow-message --approve REF --approved-by LOGIN]
 * Output is sanitised JSON (no Builder key, emails, wallet addresses or full Mind IDs).
 */
import { parseArgs } from "node:util";
import { loadConfig } from "../config/project.ts";
import { assertNoSecrets, shortRef } from "../lib/secrets.ts";
import { FileStore } from "../lib/store.ts";
import { privateRecordsDir } from "../lib/paths.ts";
import { builderKeyFromEnv, createServerMindsClient } from "./client.ts";
import { parseMindMapping, resolveProjectMind, type Approval } from "./authority.ts";
import { capabilities, inventory, mindDetail, telemetry } from "./ops.ts";
import { provisionMind } from "./provision.ts";
import { equipApproved } from "./equip.ts";
import { applyCirclePlan, planCircleChange } from "./circle.ts";
import { runSmokeTest } from "./smoke.ts";

const { positionals, values } = parseArgs({
  allowPositionals: true,
  options: {
    name: { type: "string" },
    archetype: { type: "string" },
    approve: { type: "string" },
    "approved-by": { type: "string" },
    skills: { type: "string" },
    apps: { type: "string" },
    add: { type: "string" },
    remove: { type: "string" },
    "mind-name": { type: "string" },
    "allow-message": { type: "boolean", default: false },
    "timeout-ms": { type: "string", default: "180000" },
  },
});

const [cmd, slug] = positionals;
const out = (o: unknown) => {
  const s = JSON.stringify(o, null, 2);
  assertNoSecrets("cli output", s, [builderKeyFromEnv() ?? ""]);
  console.log(s);
};
const list = (s: string | undefined) => (s ? s.split(",").map((x) => x.trim()).filter(Boolean) : []);
const approvalFor = (action: string): Approval | undefined =>
  values.approve && values["approved-by"] && slug ? { approvedBy: values["approved-by"], ref: values.approve, action, projectSlug: slug } : undefined;

async function main(): Promise<void> {
  if (!cmd) throw new Error("usage: minds <command> [slug] (see header)");
  const minds = createServerMindsClient();
  const cfg = loadConfig();
  if (cfg.issues.length) throw new Error(`config invalid: ${cfg.issues.map((i) => i.message).join("; ")}`);
  const mapping = parseMindMapping(process.env["MINDS_PROJECT_MAP"]);
  const need = (s: string | undefined): string => {
    if (!s) throw new Error(`${cmd} requires a project slug`);
    return s;
  };
  switch (cmd) {
    case "inventory":
      return out(await inventory(minds));
    case "project":
    case "reconcile": {
      const r = await resolveProjectMind({ cfg, mapping, slug: need(slug), operation: cmd, minds });
      return out({ project: r.project.slug, mind: await mindDetail(minds, r.mindId), mappingVersion: r.mapping.configVersion });
    }
    case "telemetry": {
      const r = await resolveProjectMind({ cfg, mapping, slug: need(slug), operation: "telemetry", minds });
      return out({ project: r.project.slug, ...(await telemetry(minds, r.mindId)) });
    }
    case "capabilities": {
      const r = await resolveProjectMind({ cfg, mapping, slug: need(slug), operation: "capabilities", minds });
      return out({ project: r.project.slug, ...(await capabilities(minds, r.mindId)) });
    }
    case "provision": {
      const s = need(slug);
      const p = cfg.projects.find((x) => x.slug === s);
      if (!p) throw new Error(`unknown project ${s}`);
      const approval = approvalFor("provision");
      const { authoriseOperation } = await import("./authority.ts");
      authoriseOperation(cfg.policies.get(p.policyVersion)!, "provision", s, approval);
      if (!values.name || !values.archetype) throw new Error("--name and --archetype are required");
      const store = new FileStore(privateRecordsDir());
      const rec = await provisionMind(minds, store, { slug: s, projectId: p.projectId, name: values.name, archetype: values.archetype, approvalRef: approval!.ref });
      return out({ project: s, state: rec.state, mind: rec.mindId ? shortRef(rec.mindId) : null, next: rec.state === "mind-confirmed" ? "record the mapping in the protected MINDS_PROJECT_MAP secret, then set mind.mappingStatus=approved via a reviewed PR" : "operator review required" });
    }
    case "equip": {
      const r = await resolveProjectMind({ cfg, mapping, slug: need(slug), operation: "equip", approval: approvalFor("equip"), minds });
      const reports = [];
      if (values.skills) reports.push(await equipApproved(minds, r.mindId, "skills", list(values.skills)));
      if (values.apps) reports.push(await equipApproved(minds, r.mindId, "apps", list(values.apps)));
      out({ project: r.project.slug, reports });
      if (reports.some((x) => !x.complete)) process.exitCode = 2;
      return;
    }
    case "circle": {
      const action = values.remove && !values.add ? "circle-remove" : "circle-add";
      const r = await resolveProjectMind({ cfg, mapping, slug: need(slug), operation: action, approval: approvalFor(action), minds });
      const approved = list(process.env["SC_CIRCLE_APPROVED_MEMBERS"]);
      const plan = planCircleChange(await minds.getCircle(r.mindId), list(values.add), list(values.remove), { approvedMembers: approved });
      const audit = await applyCirclePlan(minds, r.mindId, plan, approvalFor(action));
      return out({ project: r.project.slug, changes: audit.length, allConfirmed: audit.every((a) => a.confirmedInFinalState) });
    }
    case "pause":
    case "resume": {
      const r = await resolveProjectMind({ cfg, mapping, slug: need(slug), operation: cmd, approval: approvalFor(cmd), minds });
      const res = await minds.updateMindStatus(r.mindId, { isEnabled: cmd === "resume" });
      const after = await minds.getMind(r.mindId);
      return out({ project: r.project.slug, ack: res.result, isEnabledAfter: after.isEnabled ?? null });
    }
    case "smoke-test": {
      const name = values["mind-name"];
      if (!name) throw new Error("smoke-test needs an explicit --mind-name (the first Mind is never picked automatically)");
      const testRef = Object.values(mapping).find((m) => m.role === "test" && m.testMind === true);
      const matches = (await minds.listMinds()).filter((m) => m.name === name);
      if (matches.length !== 1) throw new Error(`expected exactly one Mind named ${name}, found ${matches.length}`);
      const target = matches[0]!;
      const designated = Boolean(testRef && testRef.mindId === target.mindId);
      if (values["allow-message"] && !values.approve) throw new Error("--allow-message requires --approve <ref>");
      const res = await runSmokeTest(minds, { testMindId: target.mindId, expectedName: name, allowMessage: values["allow-message"] ?? false, designatedTestMind: designated, timeoutMs: Number(values["timeout-ms"]), runId: process.env["GITHUB_RUN_ID"] ?? String(Date.now()) });
      out({ at: new Date().toISOString(), ...res });
      if (res.steps.some((s) => s.status === "FAIL")) process.exitCode = 1;
      return;
    }
    default:
      throw new Error(`unknown command ${cmd}`);
  }
}

main().catch((e: unknown) => {
  const msg = e instanceof Error ? e.message : String(e);
  console.error(`minds ${cmd ?? ""}: ${msg.replace(/eyJ[A-Za-z0-9._-]+/g, "[REDACTED]")}`);
  process.exit(1);
});
