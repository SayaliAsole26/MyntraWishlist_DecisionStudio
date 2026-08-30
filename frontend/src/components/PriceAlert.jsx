import { formatPrice } from "../api/client.js";

export default function PriceAlert({ alert, onDismiss, onViewItem }) {
  const { product, payload } = alert;
  if (!product) return null;

  const saveAmount = payload.save_amount ?? payload.from - payload.to;

  return (
    <article className="alert-card alert-card--price">
      <div className="alert-card-icon" aria-hidden>
        ↓
      </div>
      <div className="alert-card-body">
        <p className="alert-card-title">Price drop on your saved item</p>
        <p className="alert-card-product">
          {product.brand} — {product.name}
        </p>
        <p className="alert-card-detail">
          Was {formatPrice(payload.from)} · Now {formatPrice(payload.to)} · Save {formatPrice(saveAmount)}
        </p>
      </div>
      <div className="alert-card-actions">
        <button type="button" className="btn btn-primary btn-sm" onClick={() => onViewItem(product.product_id)}>
          View item
        </button>
        <button type="button" className="btn btn-ghost btn-sm" onClick={() => onDismiss(alert.alert_id)}>
          Dismiss
        </button>
      </div>
    </article>
  );
}
