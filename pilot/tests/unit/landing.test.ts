// The landing page's campus hero (scripts/landing.py) must show exactly the projects the public campus
// projection shows, with the demonstration label, and its script must make no calls other than the
// public projection and the lazily loaded 3D bundle.
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { buildCampusData } from "../../src/campus/projection.ts";
import { PUBLIC_RECORDS_DIR, REPO_ROOT } from "../../src/lib/paths.ts";
import { cfg } from "../fixtures/helpers.ts";

const py = (code: string) => execFileSync("python3", ["-c", code], { cwd: join(REPO_ROOT, "scripts"), encoding: "utf8" });

test("landing campus hero lists the same projects as the public projection", () => {
  const fromPy = JSON.parse(py("import json, landing; print(json.dumps(landing.campus_projects()))")) as Array<Record<string, unknown>>;
  const data = buildCampusData(cfg().projects, PUBLIC_RECORDS_DIR, "https://github.com/Blockchains/sol-college/blob/main");
  assert.deepEqual(fromPy.map((p) => p["slug"]).sort(), data.projects.map((p) => p.slug).sort());
  for (const p of data.projects) {
    const q = fromPy.find((x) => x["slug"] === p.slug)!;
    assert.equal(q["displayName"], p.displayName);
    assert.equal(q["sector"], p.sector);
    assert.equal(q["demonstration"], p.ownership === "sol-college-demonstration");
    assert.deepEqual(Object.keys(q).sort(), ["demonstration", "demonstrationNotice", "description", "displayName", "sector", "slug"]);
  }
});

test("landing campus hero renders first, labels demonstrations, links to /campus/", () => {
  const html = py("import landing; print(landing.campus_hero_html(landing.campus_projects()))");
  const tpl = readFileSync(join(REPO_ROOT, "scripts/landing.html"), "utf8");
  assert.ok(tpl.indexOf("{{CAMPUS_HERO}}") < tpl.indexOf('id="learn"'), "campus hero must precede the existing hero");
  assert.match(html, /href="\/campus\/">Explore campus</);
  assert.match(html, /class="ch-demo">Demo</);
  assert.equal((html.match(/class="ch-room /g) ?? []).length, 3);
  assert.doesNotMatch(html, /[\w.+-]+@[\w-]+\.[a-z]{2,}|"reviewers"|mappingRef|accountId|configVersion/i);
});

test("landing campus script only fetches the public projection and the 3D bundle", () => {
  const js = readFileSync(join(REPO_ROOT, "scripts/landing-campus.js"), "utf8");
  const urls = [...js.matchAll(/(?:fetch|import)\(\s*'([^']+)'/g)].map((m) => m[1]);
  assert.deepEqual(urls.sort(), ["/campus/campus3d.js", "/campus/data.json"]);
  assert.match(js, /prefers-reduced-motion: reduce/);
  assert.match(js, /pointer: coarse/);
});
