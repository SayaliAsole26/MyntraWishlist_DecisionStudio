import { formatPrice } from "../api/client.js";

const COMPACT_METRICS = new Set(["price", "rating"]);

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
              <td>{row.label}</td>
              {ids.map((pid) => {
                const val = row.values?.[pid];
                let display = val;
                if (row.metric === "price") display = formatPrice(val);
                else if (val == null) display = "—";
                else if (typeof val === "number" && row.metric.includes("score")) {
                  display = val.toFixed(2);
                }
                return <td key={pid}>{display}</td>;
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
