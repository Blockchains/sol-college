import { loadConfig } from "./project.ts";

const cfg = loadConfig();
for (const i of cfg.issues) console.error(`config error: ${i.file}: ${i.message}`);
console.log(JSON.stringify({ liveProjects: cfg.projects.map((p) => p.slug), excludedPlaceholders: cfg.excludedPlaceholders, policies: [...cfg.policies.keys()], errors: cfg.issues.length }));
process.exit(cfg.issues.length ? 1 : 0);
