import { Link } from "react-router-dom";
import { formatPrice } from "../api/client.js";
import { friendlyError } from "../lib/friendlyError.js";
import ComparisonTable from "./ComparisonTable.jsx";

export default function CompareDrawer({ open, onClose, result, loading, error, fromCount }) {
  if (!open) return null;

  const ids = result?.products?.map((p) => p.product_id).join(",") || "";
  const bestId = result?.labels?.best_balance;
  const bestProduct = result?.products?.find((p) => p.product_id === bestId);
  const errText = friendlyError(error, null);

  return (
    <div className="sheet-backdrop" onClick={onClose} role="presentation">
      <div
        className="sheet compare-sheet sheet-enter"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-label="Compare products"
      >
        <div className="sheet-header">
          <h2>Quick compare</h2>
          <button type="button" className="btn btn-ghost btn-sm" onClick={onClose}>
            Close
          </button>
        </div>

        {loading ? <p className="muted sheet-body">Building comparison…</p> : null}
        {errText && !result ? <p className="error-banner sheet-body">{errText}</p> : null}

        {result ? (
          <div className="sheet-body">
            {bestProduct ? (
              <p className="compare-pick">
                Top pick: <strong>{bestProduct.brand}</strong> — {formatPrice(bestProduct.price)}
              </p>
            ) : null}

            <ComparisonTable
              rows={result.rows}
              products={result.products}
              labels={result.labels}
              compact
            />

            {ids ? (
              <Link
                to={`/decision-studio?ids=${ids}${fromCount ? `&from=${fromCount}` : ""}`}
                className="btn btn-primary compare-full-link"
                onClick={onClose}
              >
                View full analysis
              </Link>
            ) : null}
          </div>
        ) : null}
      </div>
    </div>
  );
}
