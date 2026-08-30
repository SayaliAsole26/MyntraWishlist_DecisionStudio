const STORAGE_KEY = "decisionStudioContext";

export const NEED_OPTIONS = [
  { id: "Workwear", label: "Workwear" },
  { id: "Casual", label: "Casual everyday" },
  { id: "Party", label: "Party / Festive" },
  { id: "Sports", label: "Sports" },
  { id: "Vacation", label: "Vacation" },
];

export const TRADEOFF_OPTIONS = [
  { id: "FIT", label: "Fit" },
  { id: "VALUE", label: "Value" },
  { id: "QUALITY", label: "Quality" },
  { id: "VERSATILITY", label: "Versatility" },
];

export const CONFIDENCE_LABELS = ["Not sure", "Unsure", "Somewhat sure", "Sure", "Very sure"];

const DEFAULTS = {
  need: "Workwear",
  tradeoff: "QUALITY",
  confidence: 2,
};

export function getDecisionContext() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { ...DEFAULTS };
    return { ...DEFAULTS, ...JSON.parse(raw) };
  } catch {
    return { ...DEFAULTS };
  }
}

export function saveDecisionContext(partial) {
  const next = { ...getDecisionContext(), ...partial };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  return next;
}

export function compareOptionsFromContext(ctx = getDecisionContext()) {
  return {
    need: ctx.need || null,
    tradeoff_priority: ctx.tradeoff || null,
    user_confidence: ctx.confidence ?? null,
  };
}
