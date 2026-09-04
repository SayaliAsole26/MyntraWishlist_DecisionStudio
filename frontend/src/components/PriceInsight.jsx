import { formatPrice } from "../api/client.js";
import { friendlyError } from "../lib/friendlyError.js";

export default function PriceInsight({ open, onClose, data, loading, error }) {
  if (!open) return null;
  const errText = friendlyError(error, null);

  return (
    <div className="sheet-backdrop" onClick={onClose} role="presentation">
      <div className="sheet insight-sheet sheet-enter" onClick={(e) => e.stopPropagation()} role="dialog" aria-label="Price insight">
        <div className="sheet-header">
          <h2>Price insight</h2>
          <button type="button" className="btn btn-ghost btn-sm" onClick={onClose}>
            Close
          </button>
        </div>
        <div className="sheet-body">
          {loading ? <p className="muted">Loading…</p> : null}
          {errText && !data ? <p className="error-banner">{errText}</p> : null}
          {data ? (
            <>
              <p className="insight-lead">{data.summary}</p>
              <dl className="insight-facts">
                <div>
                  <dt>Current</dt>
                  <dd>{formatPrice(data.current_price)}</dd>
                </div>
                {data.saved_price != null ? (
                  <div>
                    <dt>Saved at</dt>
                    <dd>{formatPrice(data.saved_price)}</dd>
                  </div>
                ) : null}
                {data.min_price != null ? (
                  <div>
                    <dt>Recent low</dt>
                    <dd>{formatPrice(data.min_price)}</dd>
                  </div>
                ) : null}
                {data.max_price != null ? (
                  <div>
                    <dt>Recent high</dt>
                    <dd>{formatPrice(data.max_price)}</dd>
                  </div>
                ) : null}
              </dl>
              {!data.history_available ? (
                <p className="muted small">Price history unavailable.</p>
              ) : null}
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}
