import { useEffect, useState } from "react";
import { api } from "../api/client.js";

const BASE_OCCASIONS = [
  "Casual",
  "Office",
  "Sports",
  "Vacation",
  "Party",
  "Festive",
  "Everyday",
  "General",
];

export default function WishlistOccasionModal({ open, onConfirm, onCancel }) {
  const [occasion, setOccasion] = useState("Casual");
  const [options, setOptions] = useState(BASE_OCCASIONS);

  useEffect(() => {
    if (!open) return;
    setOccasion("Casual");
    api
      .getProfile()
      .then((profile) => {
        const preferred = profile?.occasions || [];
        const merged = [...new Set([...preferred, ...BASE_OCCASIONS])];
        setOptions(merged);
        if (preferred.length) {
          setOccasion(preferred[0]);
        }
      })
      .catch(() => setOptions(BASE_OCCASIONS));
  }, [open]);

  if (!open) return null;

  return (
    <div className="sheet-backdrop" onClick={onCancel} role="presentation">
      <div
        className="sheet occasion-sheet sheet-enter"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-label="Save to Wishlist"
      >
        <div className="sheet-header">
          <h2>Save to Wishlist</h2>
          <button type="button" className="btn btn-ghost btn-sm" onClick={onCancel}>
            Cancel
          </button>
        </div>
        <div className="sheet-body">
          <p className="muted small">Choose an occasion folder for this item.</p>
          <fieldset className="occasion-options">
            {options.map((o) => (
              <label key={o} className="question-option">
                <input
                  type="radio"
                  name="occasion"
                  value={o}
                  checked={occasion === o}
                  onChange={() => setOccasion(o)}
                />
                <span>{o}</span>
              </label>
            ))}
          </fieldset>
          <button type="button" className="btn btn-primary" onClick={() => onConfirm(occasion)}>
            Add to Wishlist
          </button>
        </div>
      </div>
    </div>
  );
}
