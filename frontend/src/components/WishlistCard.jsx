import ProductImage from "./ProductImage.jsx";
import { forwardRef } from "react";
import { Link } from "react-router-dom";
import { formatPrice } from "../api/client.js";

const WishlistCard = forwardRef(function WishlistCard(
  {
    item,
    selected,
    onToggleSelect,
    onRemove,
    onAddToBag,
    onPriceInsight,
    onReviewInsight,
    inBag = false,
  },
  ref
) {
  const { product, signals = [], concerns = [] } = item;

  return (
    <li ref={ref} className={`wishlist-card ${selected ? "wishlist-card--selected" : ""}`}>
      <label className="wishlist-select">
        <input
          type="checkbox"
          checked={selected}
          onChange={() => onToggleSelect(item.product_id)}
          aria-label={`Select ${product.name} for compare`}
        />
      </label>

      <Link to={`/product/${item.product_id}`} className="wishlist-card-thumb">
        <ProductImage src={product.image_url} alt={product.name} />
      </Link>

      <div className="wishlist-card-body">
        <p className="product-brand">{product.brand}</p>
        <Link to={`/product/${item.product_id}`} className="wishlist-card-title">
          {product.name}
        </Link>
        <p className="product-price">{formatPrice(product.price)}</p>
        {item.size ? <p className="wishlist-size-tag">Size: {item.size}</p> : null}
        <p className="muted small">Saved at {formatPrice(item.saved_price)}</p>

        {signals.length > 0 ? (
          <div className="signal-row">
            {signals.map((s) => (
              <span key={s} className="signal-badge signal-badge--positive">
                {s}
              </span>
            ))}
          </div>
        ) : null}

        {concerns.length > 0 ? (
          <div className="signal-row">
            {concerns.map((c) => (
              <span key={c} className="signal-badge signal-badge--concern">
                {c}
              </span>
            ))}
          </div>
        ) : null}

        <div className="insight-links">
          <button type="button" className="link-btn" onClick={() => onPriceInsight(item.product_id)}>
            Price insight
          </button>
          <button type="button" className="link-btn" onClick={() => onReviewInsight(item.product_id)}>
            Based on buyer reviews
          </button>
        </div>
      </div>

      <div className="wishlist-card-actions">
        <button
          type="button"
          className={inBag ? "btn btn-added btn-sm" : "btn btn-secondary btn-sm"}
          onClick={() => onAddToBag(item.product_id)}
          disabled={inBag}
        >
          {inBag ? "Added to Bag" : "Add to Bag"}
        </button>
        <button type="button" className="btn btn-ghost btn-sm" onClick={() => onRemove(item.product_id)}>
          Remove
        </button>
      </div>
    </li>
  );
});

export default WishlistCard;
