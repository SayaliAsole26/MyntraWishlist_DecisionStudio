import { Link } from "react-router-dom";
import { formatPrice } from "../api/client.js";

export default function CheckoutConfirmation({ order, onClose }) {
  if (!order) return null;

  return (
    <div className="sheet-backdrop checkout-backdrop" onClick={onClose} role="presentation">
      <div
        className="sheet checkout-sheet sheet-enter"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-label="Order confirmed"
      >
        <div className="sheet-header">
          <h2>Order confirmed</h2>
          <button type="button" className="btn btn-ghost btn-sm" onClick={onClose}>
            Close
          </button>
        </div>
        <div className="sheet-body checkout-confirm">
          <div className="checkout-success-icon" aria-hidden>
            ✓
          </div>
          <p className="checkout-lede">Thank you — your purchase is complete.</p>
          <dl className="checkout-details">
            <div>
              <dt>Order ID</dt>
              <dd>{order.order_id}</dd>
            </div>
            <div>
              <dt>Items</dt>
              <dd>{order.item_count}</dd>
            </div>
            <div>
              <dt>Total paid</dt>
              <dd>{formatPrice(order.total)}</dd>
            </div>
          </dl>
          <p className="muted small">Order saved locally for this demo.</p>
          <div className="checkout-actions">
            <Link to="/products" className="btn btn-primary" onClick={onClose}>
              Continue shopping
            </Link>
            <Link to="/wishlist" className="btn btn-secondary" onClick={onClose}>
              Back to Wishlist
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
