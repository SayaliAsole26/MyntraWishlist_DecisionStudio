import { Link } from "react-router-dom";
import { formatPrice } from "../api/client.js";
import ProductImage from "./ProductImage.jsx";
import WishlistHeart from "./WishlistHeart.jsx";

export default function ProductCard({ product, inWishlist = false, onWishlistToggle }) {
  return (
    <article className="product-card">
      <div className="product-card-image">
        <Link to={`/product/${product.product_id}`} className="product-card-image-link">
          <ProductImage src={product.image_url} alt={product.name} />
        </Link>
        <WishlistHeart
          productId={product.product_id}
          saved={inWishlist}
          onToggle={() => onWishlistToggle?.(product)}
        />
      </div>
      <Link to={`/product/${product.product_id}`} className="product-card-body">
        <p className="product-brand">{product.brand}</p>
        <h3 className="product-name">{product.name}</h3>
        <div className="product-meta">
          <span className="product-price">{formatPrice(product.price)}</span>
          {product.mrp > product.price ? (
            <span className="product-mrp">{formatPrice(product.mrp)}</span>
          ) : null}
        </div>
        {product.rating ? (
          <p className="product-rating">
            ★ {product.rating.toFixed(1)}
            {product.rating_count ? (
              <span className="muted"> ({product.rating_count.toLocaleString("en-IN")})</span>
            ) : null}
          </p>
        ) : null}
      </Link>
    </article>
  );
}
