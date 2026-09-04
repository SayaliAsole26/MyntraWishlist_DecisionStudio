import { formatPrice } from "../api/client.js";

const COMPACT_METRICS = new Set(["price", "rating"]);

const SCORE_METRICS = new Set([
  "need_fit_score",
  "value_score",
  "fit_score",
  "quality_score",
]);

const ROW_LABELS = {
  need_fit_score: "Need fit",
  value_score: "Value",
  fit_score: "Fit",
  quality_score: "Quality",
};

/** Map 0–1 scores to short, color-coded tags (relative within the row). */
function scoreTag(metric, value, rowValues) {
  if (value == null || Number.isNaN(Number(value))) {
    return { text: "No data", tier: "muted" };
  }
  const num = Number(value);
  const peers = Object.values(rowValues || {})
    .filter((v) => v != null && !Number.isNaN(Number(v)))
    .map(Number)
    .sort((a, b) => b - a);

  const best = peers[0];
  const worst = peers[peers.length - 1];
  const isBest = num === best;
  const isWorst = peers.length > 1 && num === worst && best !== worst;
  const isHigh = isBest || num >= 0.85;
  const isLow = isWorst || num < 0.45;

  const copy = {
    need_fit_score: {
      high: "Perfect Match",
      mid: "Good Match",
      low: "Weak Match",
    },
    value_score: {
      high: "Great Value",
      mid: "Fair Value",
      low: "Pricey",
    },
    fit_score: {
      high: "Excellent Fit",
      mid: "Decent Fit",
      low: "Fit Risk",
    },
    quality_score: {
      high: "Top Rated",
      mid: "Solid",
      low: "Weak Signal",
    },
  }[metric] || { high: "Strong", mid: "Okay", low: "Weak" };

  if (isHigh) return { text: copy.high, tier: "high" };
  if (isLow) return { text: copy.low, tier: "low" };
  return { text: copy.mid, tier: "mid" };
}

export default function ComparisonTable({ rows, products, labels, compact = false }) {
  if (!rows?.length || !products?.length) return null;

  const displayRows = compact ? rows.filter((r) => COMPACT_METRICS.has(r.metric)) : rows;

  const ids = products.map((p) => p.product_id);

  const labelFor = (pid) => {
    if (!labels) return null;
    const tags = [];
    if (labels.best_value === pid) tags.push("Best value");
    if (labels.best_reviewed === pid) tags.push("Best reviewed");
    if (labels.best_balance === pid) tags.push("Best balance");
    return tags;
  };

  return (
    <div className="compare-table-wrap">
      <table className="compare-table">
        <thead>
          <tr>
            <th>Metric</th>
            {products.map((p) => (
              <th key={p.product_id}>
                <span className="compare-product-name">{p.brand}</span>
                {labelFor(p.product_id)?.map((t) => (
                  <span key={t} className="compare-tag">
                    {t}
                  </span>
                ))}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {displayRows.map((row) => (
            <tr key={row.metric}>
              <td>{ROW_LABELS[row.metric] || row.label}</td>
              {ids.map((pid) => {
                const val = row.values?.[pid];
                if (SCORE_METRICS.has(row.metric)) {
                  const tag = scoreTag(row.metric, val, row.values);
                  return (
                    <td key={pid}>
                      <span className={`score-tag score-tag--${tag.tier}`}>{tag.text}</span>
                    </td>
                  );
                }
                let display = val;
                if (row.metric === "price") display = formatPrice(val);
                else if (val == null) display = "—";
                return <td key={pid}>{display}</td>;
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
