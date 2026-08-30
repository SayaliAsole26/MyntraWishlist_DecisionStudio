import { useEffect, useState } from "react";
import { getSizeInfo, sizeGuideLabel } from "../lib/sizeGuide.js";

export default function WishlistSizeModal({ open, product, onConfirm, onCancel }) {
  const [size, setSize] = useState(null);

  useEffect(() => {
    if (!open || !product) return;
    setSize(product.sizes?.[0] ?? null);
  }, [open, product?.product_id, product?.sizes]);

  if (!open || !product?.sizes?.length) return null;

  return (
    <div className="sheet-backdrop" onClick={onCancel} role="presentation">
      <div
        className="sheet occasion-sheet sheet-enter"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-label="Choose size"
      >
        <div className="sheet-header">
          <h2>Choose size</h2>
          <button type="button" className="btn btn-ghost btn-sm" onClick={onCancel}>
            Cancel
          </button>
        </div>
        <div className="sheet-body">
          <p className="muted small">
            {product.brand} — {product.name}
          </p>
          <p className="muted small">{sizeGuideLabel(product)}</p>
          <div className="size-row wishlist-size-options">
            {product.sizes.map((s) => (
              <button
                key={s}
                type="button"
                className={`size-pill size-pill-btn${size === s ? " size-pill-active" : ""}`}
                aria-pressed={size === s}
                onClick={() => setSize(s)}
              >
                {s}
              </button>
            ))}
          </div>
          {size ? <p className="size-info">{getSizeInfo(product, size)}</p> : null}
          <button
            type="button"
            className="btn btn-primary"
            disabled={!size}
            onClick={() => size && onConfirm(size)}
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  );
}
