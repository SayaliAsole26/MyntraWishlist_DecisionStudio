/** Map technical API failures to short, user-facing copy. Never show HTTP codes or infra hints. */
const FRIENDLY_DEFAULT = "Something went wrong. Please try again.";

const PATTERNS = [
  { test: /alert not found|already dismissed/i, message: null }, // silent — not user-facing
  { test: /cannot reach api|failed to fetch|networkerror|proxy failed|railway|vite_api|cors/i, message: "Connection issue. Please try again." },
  { test: /http\s*\d{3}|\b404\b|\b500\b|\b502\b|\b503\b/i, message: FRIENDLY_DEFAULT },
  { test: /not found/i, message: "We couldn't find that. Please try again." },
  { test: /timeout|timed out/i, message: "That took too long. Please try again." },
];

export function friendlyError(err, fallback = FRIENDLY_DEFAULT) {
  const raw =
    typeof err === "string"
      ? err
      : err?.message || err?.detail || (err != null ? String(err) : "");

  if (!raw || !String(raw).trim()) return fallback;

  for (const { test, message } of PATTERNS) {
    if (test.test(raw)) return message;
  }

  // Keep short, plain product copy; drop long debug dumps.
  if (raw.length > 120 || /uvicorn|traceback|stack|vercel|localhost/i.test(raw)) {
    return fallback;
  }

  return raw;
}

/** Returns null when the failure should not be shown in the UI at all. */
export function visibleError(err, fallback = FRIENDLY_DEFAULT) {
  return friendlyError(err, fallback);
}
