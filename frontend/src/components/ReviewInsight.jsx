export default function ReviewInsight({ open, onClose, data, loading, error }) {
  if (!open) return null;

  return (
    <div className="sheet-backdrop" onClick={onClose} role="presentation">
      <div className="sheet insight-sheet sheet-enter" onClick={(e) => e.stopPropagation()} role="dialog" aria-label="Review insight">
        <div className="sheet-header">
          <h2>Based on buyer reviews</h2>
          <button type="button" className="btn btn-ghost btn-sm" onClick={onClose}>
            Close
          </button>
        </div>
        <div className="sheet-body">
          {loading ? <p className="muted">Loading…</p> : null}
          {error ? <p className="error-banner">{error}</p> : null}
          {data ? (
            <>
              <p className="insight-lead">{data.summary}</p>
              <p className="muted small">
                Based on {data.review_count} available review{data.review_count === 1 ? "" : "s"} ·{" "}
                {data.confidence} confidence
              </p>
              {data.likes?.length ? (
                <div className="insight-section">
                  <h3>Positive themes</h3>
                  <div className="signal-row">
                    {data.likes.map((t) => (
                      <span key={t} className="signal-badge signal-badge--positive">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              ) : null}
              {data.concerns?.length ? (
                <div className="insight-section">
                  <h3>Concerns</h3>
                  <div className="signal-row">
                    {data.concerns.map((t) => (
                      <span key={t} className="signal-badge signal-badge--concern">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              ) : null}
              {!data.available ? (
                <p className="muted small">Not enough review data to assess this reliably.</p>
              ) : null}
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}
