import { Link } from "react-router-dom";
import { formatPrice } from "../api/client.js";

export default function SimilarProductAlert({ alert, onDismiss, onCompare }) {
  const { product, similar_product, payload } = alert;
  const alt = similar_product;
  if (!product || !alt) return null;

  const benefits = payload.benefits?.length
    ? payload.benefits.join(" · ")
    : payload.reason;

  return (
    <article className="alert-card alert-card--similar">
      <div className="alert-card-body">
        <p className="alert-card-title">Similar option worth a look</p>
        <p className="alert-card-product">
          For your saved {product.brand} item, consider {alt.brand} — {alt.name}
        </p>
        <p className="alert-card-detail">
          {formatPrice(alt.price)}
          {alt.rating ? ` · ★ ${alt.rating}` : ""}
          {benefits ? ` · ${benefits}` : ""}
        </p>
        {payload.reason ? <p className="muted small">{payload.reason}</p> : null}
      </div>
      <div className="alert-card-actions">
        <button
          type="button"
          className="btn btn-primary btn-sm"
          onClick={() => onCompare([product.product_id, alt.product_id])}
        >
          Compare
        </button>
        <Link to={`/products/${alt.product_id}`} className="btn btn-secondary btn-sm">
          View item
        </Link>
        <button type="button" className="btn btn-ghost btn-sm" onClick={() => onDismiss(alert.alert_id)}>
          Dismiss
        </button>
      </div>
    </article>
  );
}
