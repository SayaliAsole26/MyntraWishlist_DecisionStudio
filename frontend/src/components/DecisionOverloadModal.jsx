import { useEffect, useState } from "react";

function groupTitle(group) {
  if (group.category) return group.category;
  const label = group.label || "items";
  return label.charAt(0).toUpperCase() + label.slice(1);
}

export default function DecisionOverloadModal({ overloads = [], onCompare, onDismiss }) {
  const [selectedKey, setSelectedKey] = useState(null);

  useEffect(() => {
    if (overloads.length === 1) {
      setSelectedKey(overloads[0].group_key);
    } else if (overloads.length > 1) {
      setSelectedKey(null);
    }
  }, [overloads]);

  if (!overloads.length) return null;

  const multi = overloads.length > 1;
  const selected =
    overloads.find((o) => o.group_key === selectedKey) || (multi ? null : overloads[0]);

  return (
    <div className="sheet-backdrop overload-backdrop" role="presentation">
      <div className="sheet overload-sheet sheet-enter" role="dialog" aria-label="Decision overload">
        <div className="sheet-header">
          <h2>Too many similar saves?</h2>
        </div>
        <div className="sheet-body">
          {multi ? (
            <>
              <p className="overload-copy">
                You have similar items in more than one category. Choose which group to narrow
                down:
              </p>
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
            </>
          ) : (
            <p className="overload-copy">
              You have {selected.count} similar {selected.label} saved. Want help narrowing them
              down?
            </p>
          )}

          <div className="overload-actions">
            <button
              type="button"
              className="btn btn-primary"
              disabled={!selected}
              onClick={() =>
                selected &&
                onCompare(selected.product_ids, selected.alert_id, selected.group_key)
              }
            >
              Narrow them down
            </button>
            {selected?.alert_id ? (
              <button type="button" className="btn btn-ghost" onClick={() => onDismiss(selected.alert_id)}>
                Dismiss
              </button>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
