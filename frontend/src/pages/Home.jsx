import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client.js";
import ProductCard from "../components/ProductCard.jsx";
import WishlistAddModals from "../components/WishlistAddModals.jsx";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingState from "../components/LoadingState.jsx";
import { useWishlistAdd } from "../hooks/useWishlistAdd.js";
import { useToast } from "../state/ToastContext.jsx";

export default function Home() {
  const { showToast } = useToast();
  const { ids: wishlistIds, addStep, pendingProduct, handleToggle, confirmSize, confirmAdd, cancelAdd } =
    useWishlistAdd(showToast);
  const [categories, setCategories] = useState([]);
  const [featured, setFeatured] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    setLoading(true);
    Promise.all([api.getCategories(), api.getProducts()])
      .then(([cats, prods]) => {
        setCategories(cats);
        setFeatured(prods.products.slice(0, 6));
        setError("");
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <section className="page">
      <div className="hero">
        <h1>Shop smarter from your Wishlist</h1>
        <p className="lede">Browse fashion picks and save what you like.</p>
      </div>

      {loading ? <LoadingState message="Loading storefront…" /> : null}
      <ErrorBanner message={!loading ? error : ""} onRetry={error ? load : undefined} />

      {!loading && !error ? (
        <>
          <section className="section">
            <h2>Shop by category</h2>
            {categories.length === 0 ? (
              <EmptyState
                title="Catalog not loaded yet. Run ingest from the README demo script."
                action={
                  <button type="button" className="btn btn-secondary btn-sm" onClick={load}>
                    Retry
                  </button>
                }
              />
            ) : (
              <div className="category-chips">
                {categories.map((c) => (
                  <Link key={c.name} to={`/products?category=${encodeURIComponent(c.name)}`} className="chip">
                    {c.name} <span className="chip-count">{c.count}</span>
                  </Link>
                ))}
              </div>
            )}
          </section>

          <section className="section">
            <div className="section-head">
              <h2>Featured</h2>
              <Link to="/products" className="text-link">
                View all
              </Link>
            </div>
            {featured.length === 0 ? (
              <p className="muted">No products available.</p>
            ) : (
              <div className="product-grid">
                {featured.map((p) => (
                  <ProductCard
                    key={p.product_id}
                    product={p}
                    inWishlist={wishlistIds.has(p.product_id)}
                    onWishlistToggle={(p) => handleToggle(p)}
                  />
                ))}
              </div>
            )}
          </section>
        </>
      ) : null}

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
