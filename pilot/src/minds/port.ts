import type { MindsClient } from "@animocabrands/minds-client-lib";

/**
 * The subset of the official SDK client this pilot uses. Typed directly from the installed
 * @animocabrands/minds-client-lib MindsClient interface so fakes in tests cannot drift from the
 * real method signatures and response shapes.
 */
export type MindsPort = Pick<
  MindsClient,
  | "listMinds"
  | "getMind"
  | "checkMindName"
  | "awakenMind"
  | "updateMindStatus"
  | "getCognitionBalance"
  | "getCognitionUsage"
  | "getCognitionUsageByTool"
  | "listEquippedSkills"
  | "equipSkills"
  | "unequipSkills"
  | "listEquippedApps"
  | "equipApps"
  | "unequipApps"
  | "getCircle"
  | "addCircleMembers"
  | "removeCircleMembers"
  | "ensureConversation"
  | "getConversation"
  | "listConversations"
  | "sendMessage"
  | "getHistory"
  | "getLatestHistoryFingerprint"
  | "waitForReply"
> & { readonly bazaar: Pick<MindsClient["bazaar"], "listSkills" | "getSkill" | "listApps" | "getApp"> };

export type BazaarPort = MindsPort["bazaar"];
