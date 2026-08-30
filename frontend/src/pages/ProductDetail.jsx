import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, formatPrice } from "../api/client.js";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingState from "../components/LoadingState.jsx";
import ProductImage from "../components/ProductImage.jsx";
import WishlistHeart from "../components/WishlistHeart.jsx";
import WishlistAddModals from "../components/WishlistAddModals.jsx";
import { useBagIds } from "../hooks/useBagIds.js";
import { useWishlistAdd } from "../hooks/useWishlistAdd.js";
import { getSizeInfo, sizeGuideLabel } from "../lib/sizeGuide.js";
import { useToast } from "../state/ToastContext.jsx";

export default function ProductDetail() {
  const { productId } = useParams();
  const { showToast } = useToast();
  const { ids: wishlistIds, addStep, pendingProduct, handleToggle, confirmSize, confirmAdd, cancelAdd } =
    useWishlistAdd(showToast);
  const { has: inBag, add: addToBagIds, refresh: refreshBag } = useBagIds();
  const [product, setProduct] = useState(null);
  const [selectedSize, setSelectedSize] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    api
      .getProduct(productId)
      .then((p) => {
        setProduct(p);
        setError("");
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [productId]);

  useEffect(() => {
    load();
    refreshBag();
  }, [load, refreshBag]);

  useEffect(() => {
    setSelectedSize(product?.sizes?.[0] ?? null);
  }, [product?.product_id, product?.sizes]);

  const addWishlist = async () => {
    if (wishlistIds.has(productId)) {
      await handleToggle(productId);
      return;
    }
    await handleToggle(product);
  };

  if (loading) {
    return (
      <section className="page">
        <LoadingState message="Loading product…" />
      </section>
    );
  }

  if (error || !product) {
    return (
      <section className="page">
        <ErrorBanner message={error || "Product not found."} onRetry={load} />
        <Link to="/products" className="text-link">
          Back to products
        </Link>
      </section>
    );
  }

  const bagAdded = inBag(productId);

  const addBag = async () => {
    if (inBag(productId)) return;
    if (product.sizes?.length && !selectedSize) {
      showToast("Please select a size");
      return;
    }
    setBusy(true);
    try {
      await addToBagIds(productId);
      showToast(selectedSize ? `Added size ${selectedSize} to Bag` : "Added to Bag");
    } catch (err) {
      showToast(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="page pdp">
      <div className="pdp-grid">
        <div className="pdp-image">
          <ProductImage src={product.image_url} alt={product.name} loading="eager" />
          <WishlistHeart
            productId={product.product_id}
            saved={wishlistIds.has(product.product_id)}
            onToggle={() => handleToggle(product)}
            className="wishlist-heart--pdp"
          />
        </div>
        <div className="pdp-info">
          <p className="product-brand">{product.brand}</p>
          <h1>{product.name}</h1>
          <div className="pdp-price-row">
            <span className="product-price lg">{formatPrice(product.price)}</span>
            {product.mrp > product.price ? (
              <>
                <span className="product-mrp">{formatPrice(product.mrp)}</span>
                {product.discount ? (
                  <span className="discount-badge">{product.discount}% OFF</span>
                ) : null}
              </>
            ) : null}
          </div>
          {product.rating ? (
            <p className="product-rating">
              ★ {product.rating.toFixed(1)}
              {product.rating_count ? (
                <span className="muted"> ({product.rating_count.toLocaleString("en-IN")} ratings)</span>
              ) : null}
            </p>
          ) : null}
          {product.material ? <p className="pdp-detail"><strong>Material:</strong> {product.material}</p> : null}
          {product.fit ? <p className="pdp-detail"><strong>Fit:</strong> {product.fit}</p> : null}
          {product.sizes?.length ? (
            <div className="size-block">
              <div className="size-row">
                <strong>{sizeGuideLabel(product)}:</strong>
                {product.sizes.map((s) => (
                  <button
                    key={s}
                    type="button"
                    className={`size-pill size-pill-btn${selectedSize === s ? " size-pill-active" : ""}`}
                    aria-pressed={selectedSize === s}
                    onClick={() => setSelectedSize(s)}
                  >
                    {s}
                  </button>
                ))}
              </div>
              {selectedSize ? (
                <p className="size-info">{getSizeInfo(product, selectedSize)}</p>
              ) : null}
            </div>
          ) : null}
          <div className="pdp-actions">
            <button type="button" className="btn btn-primary" onClick={addWishlist} disabled={busy}>
              {wishlistIds.has(productId) ? "Saved to Wishlist" : "Add to Wishlist"}
            </button>
            <button
              type="button"
              className={bagAdded ? "btn btn-added" : "btn btn-secondary"}
              onClick={addBag}
              disabled={busy || bagAdded}
            >
              {bagAdded ? "Added to Bag" : "Add to Bag"}
            </button>
          </div>
        </div>
      </div>

      <WishlistAddModals
        addStep={addStep}
        pendingProduct={pendingProduct}
        onConfirmSize={confirmSize}
        onConfirmOccasion={confirmAdd}
        onCancel={cancelAdd}
      />
    </section>
  );
}
