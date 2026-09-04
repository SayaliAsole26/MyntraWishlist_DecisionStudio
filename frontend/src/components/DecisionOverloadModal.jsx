import { useEffect, useState } from "react";

function groupTitle(group) {
  const label = group.label || group.category || "items";
  return label.charAt(0).toUpperCase() + label.slice(1);
}

function OverloadIllustration() {
  return (
    <div className="overload-illustration" aria-hidden="true">
      <svg viewBox="0 0 120 72" width="96" height="58" fill="none">
        <rect x="36" y="32" width="48" height="28" rx="3" stroke="#282C3F" strokeWidth="2" />
        <path d="M36 38h48" stroke="#282C3F" strokeWidth="2" />
        <path d="M50 32V26h20v6" stroke="#282C3F" strokeWidth="2" />
        <rect x="44" y="20" width="14" height="16" rx="2" stroke="#282C3F" strokeWidth="1.8" />
        <rect x="54" y="16" width="14" height="18" rx="2" stroke="#282C3F" strokeWidth="1.8" />
        <rect x="64" y="22" width="12" height="14" rx="2" stroke="#282C3F" strokeWidth="1.8" />
      </svg>
    </div>
  );
}

/** Inline prompt — does not block wishlist buttons or navigation. */
export default function DecisionOverloadModal({ overloads = [], onCompare, onDismiss }) {
  const [selectedKey, setSelectedKey] = useState(null);

  useEffect(() => {
    if (!overloads.length) {
      setSelectedKey(null);
      return;
    }
    // Always pre-select first group so Narrow is never stuck disabled.
    setSelectedKey((prev) => {
      if (prev && overloads.some((o) => o.group_key === prev)) return prev;
      return overloads[0].group_key;
    });
  }, [overloads]);

  if (!overloads.length) return null;

  const multi = overloads.length > 1;
  const selected =
    overloads.find((o) => o.group_key === selectedKey) || overloads[0];

  return (
    <section className="overload-banner sheet-enter" aria-label="Decision overload">
      <div className="overload-banner-top">
        <OverloadIllustration />
        <div>
          <h2 className="overload-banner-title">Too many similar saves?</h2>
          {multi ? (
            <p className="overload-copy">
              Similar items in more than one category — pick a group to narrow down:
            </p>
          ) : (
            <p className="overload-copy">
              You have {selected.count} similar {selected.label} saved. Want help narrowing them
              down?
            </p>
          )}
        </div>
      </div>

      {multi ? (
        <fieldset className="overload-options">
          {overloads.map((group) => (
            <label key={group.group_key} className="question-option">
              <input
                type="radio"
                name="overload-group"
                value={group.group_key}
                checked={selectedKey === group.group_key}
                onChange={() => setSelectedKey(group.group_key)}
              />
              <span>
                {groupTitle(group)} — {group.count} saved
              </span>
            </label>
          ))}
        </fieldset>
      ) : null}

      <div className="overload-actions overload-actions--row">
        <button
          type="button"
          className="btn btn-primary"
          onClick={() =>
            selected &&
            onCompare(selected.product_ids, selected.alert_id, selected.group_key)
          }
        >
          Narrow them down
        </button>
        <button type="button" className="btn btn-ghost" onClick={() => onDismiss()}>
          Dismiss
        </button>
      </div>
    </section>
  );
}
