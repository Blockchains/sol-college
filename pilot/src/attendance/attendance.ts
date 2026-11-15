/**
 * Attendance and entitlement records. Without a verified, permitted Solana data connection the
 * pilot never marks a transfer as automatically verified; an authorised human may record a
 * manual review, which is labelled as such.
 */
export type AttendanceStatus = "pending" | "manually-reviewed-eligible" | "manually-reviewed-ineligible";

export interface AttendanceSubmission {
  developer: string;
  wallet: string;
  devnetSignature: string;
  recipient: string;
  amountLamports: number;
  window: { start: string; end: string };
  ruleVersion: string;
  status: AttendanceStatus;
  review?: { reviewer: string; at: string; note: string };
}

const SIG_RE = /^[1-9A-HJ-NP-Za-km-z]{64,90}$/;
const KEY_RE = /^[1-9A-HJ-NP-Za-km-z]{32,44}$/;

export function submitAttendance(s: Omit<AttendanceSubmission, "status" | "review">): AttendanceSubmission {
  if (!SIG_RE.test(s.devnetSignature)) throw new Error("not a base58 transaction signature");
  if (!KEY_RE.test(s.wallet) || !KEY_RE.test(s.recipient)) throw new Error("wallet/recipient must be base58 public keys");
  if (!(s.amountLamports > 0)) throw new Error("amount must be positive");
  return { ...s, status: "pending" };
}

export function manualReview(sub: AttendanceSubmission, reviewer: string, eligible: boolean, note: string, at: string, authorisedReviewers: string[]): AttendanceSubmission {
  if (!authorisedReviewers.map((r) => r.toLowerCase()).includes(reviewer.toLowerCase())) throw new Error("reviewer not authorised for attendance review");
  return { ...sub, status: eligible ? "manually-reviewed-eligible" : "manually-reviewed-ineligible", review: { reviewer, at, note } };
}

export function attendanceLabel(s: AttendanceSubmission): string {
  switch (s.status) {
    case "pending":
      return "Pending: submitted, not verified";
    case "manually-reviewed-eligible":
      return `Manually reviewed by ${s.review?.reviewer ?? "?"}: eligible (not automatically verified on-chain)`;
    case "manually-reviewed-ineligible":
      return `Manually reviewed by ${s.review?.reviewer ?? "?"}: not eligible`;
  }
}

export interface Entitlement {
  plan: string;
  status: "active" | "paused" | "expired";
  activation: "manual";
  paymentVerification: "none-manual-entitlement" | "not-applicable-demonstration";
  periodEnd?: string;
}

export function entitlementLabel(e: Entitlement, today: string): string {
  const expired = e.periodEnd !== undefined && e.periodEnd < today;
  const status = expired ? "expired" : e.status;
  const pay = e.paymentVerification === "not-applicable-demonstration" ? "demonstration project, no payment involved" : "manual entitlement, payment not verified";
  return `${e.plan}: ${status} (${pay})`;
}
