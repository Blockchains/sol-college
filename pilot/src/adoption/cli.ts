/**
 * adoption <slug> <candidateSha> <inputs.json>
 * Retrieves real GitHub evidence, verifies baseline ancestry and builds the exact manifest.
 * inputs.json: { contributions: Contribution[], narrative: Narrative, testConclusions: string[], version: number }
 */
import { readFileSync } from "node:fs";
import { loadConfig } from "../config/project.ts";
import { githubFromEnv } from "../github/api.ts";
import { createAdoptionPackage, type PackageInputs } from "./create.ts";

const [slug, sha, inputsPath] = process.argv.slice(2);
if (!slug || !sha || !inputsPath) throw new Error("usage: adoption <slug> <sha> <inputs.json>");
const inputs = JSON.parse(readFileSync(inputsPath, "utf8")) as PackageInputs;
const res = await createAdoptionPackage(githubFromEnv(), loadConfig(), slug, sha, inputs, { allowNewVersion: Boolean(process.env["SC_NEW_VERSION"]) });
if (res.outcome === "exists" && "file" in res) console.log(JSON.stringify({ outcome: "exists", file: res.file, note: "duplicate request: no new package created" }));
else console.log(JSON.stringify(res, null, 2));
