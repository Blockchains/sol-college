import type { EquipMutationResult, EquipSkillResultItem, EquipAppResultItem } from "@animocabrands/minds-client-lib";
import type { MindsPort } from "./port.ts";

export interface EquipReport {
  kind: "skills" | "apps";
  requested: string[];
  mutationConfirmed: string[];
  mutationMissing: string[];
  finalEquipped: string[];
  missingFromFinalState: string[];
  complete: boolean;
}

function norm(id: string): string {
  return id.toLowerCase();
}

/** Compare a mutation result and the re-read final equipped set against the approved IDs. */
export function assessEquipment(kind: "skills" | "apps", requested: string[], result: EquipMutationResult<EquipSkillResultItem | EquipAppResultItem>, finalIds: string[]): EquipReport {
  const req = requested.map(norm);
  const confirmed = new Set<string>();
  for (const item of result.results) {
    const id = "skillId" in item ? (item as EquipSkillResultItem).skillId : (item as EquipAppResultItem).appId;
    if (typeof id === "string" && item.isEquipped !== false) confirmed.add(norm(id));
  }
  const fin = new Set(finalIds.map(norm));
  const mutationMissing = req.filter((id) => !confirmed.has(id));
  const missingFromFinalState = req.filter((id) => !fin.has(id));
  return {
    kind,
    requested: req,
    mutationConfirmed: req.filter((id) => confirmed.has(id)),
    mutationMissing,
    finalEquipped: [...fin],
    missingFromFinalState,
    complete: missingFromFinalState.length === 0,
  };
}

export async function equipApproved(minds: Pick<MindsPort, "equipSkills" | "listEquippedSkills" | "equipApps" | "listEquippedApps">, mindId: string, kind: "skills" | "apps", ids: string[]): Promise<EquipReport> {
  if (ids.length === 0) throw new Error("no approved ids");
  if (kind === "skills") {
    const r = await minds.equipSkills(mindId, { ids });
    const fin = await minds.listEquippedSkills(mindId);
    return assessEquipment(kind, ids, r, fin.map((s) => s.skillId));
  }
  const r = await minds.equipApps(mindId, { ids });
  const fin = await minds.listEquippedApps(mindId);
  return assessEquipment(kind, ids, r, fin.map((a) => a.appId));
}
