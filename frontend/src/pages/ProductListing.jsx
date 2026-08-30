import { useCallback, useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../api/client.js";
import ProductCard from "../components/ProductCard.jsx";
import WishlistAddModals from "../components/WishlistAddModals.jsx";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingState from "../components/LoadingState.jsx";
import { useWishlistAdd } from "../hooks/useWishlistAdd.js";
import { useToast } from "../state/ToastContext.jsx";

export default function ProductListing() {
  const { showToast } = useToast();
  const { ids: wishlistIds, addStep, pendingProduct, handleToggle, confirmSize, confirmAdd, cancelAdd } =
    useWishlistAdd(showToast);
  const [searchParams] = useSearchParams();
  const category = searchParams.get("category");
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    setLoading(true);
    Promise.all([api.getProducts(category || undefined), api.getCategories()])
      .then(([data, cats]) => {
        setProducts(data.products);
        setCategories(cats);
        setError("");
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [category]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <section className="page">
      <h1>{category || "All products"}</h1>
      <div className="category-chips">
        <Link to="/products" className={`chip ${!category ? "chip-active" : ""}`}>
          All
        </Link>
        {categories.map((c) => (
          <Link
            key={c.name}
            to={`/products?category=${encodeURIComponent(c.name)}`}
            className={`chip ${category === c.name ? "chip-active" : ""}`}
          >
            {c.name}
          </Link>
        ))}
      </div>

      {loading ? <LoadingState message="Loading products…" /> : null}
      <ErrorBanner message={!loading ? error : ""} onRetry={load} />

      {!loading && !error && products.length === 0 ? (
        <EmptyState
          title={category ? `No products in ${category}.` : "No products found."}
          action={
            category ? (
              <Link to="/products" className="btn btn-secondary">
                View all products
              </Link>
            ) : (
              <button type="button" className="btn btn-secondary" onClick={load}>
                Retry
              </button>
            )
          }
        />
      ) : null}

      {!loading && products.length > 0 ? (
        <div className="product-grid">
          {products.map((p) => (
            <ProductCard
              key={p.product_id}
              product={p}
              inWishlist={wishlistIds.has(p.product_id)}
              onWishlistToggle={(p) => handleToggle(p)}
            />
          ))}
        </div>
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
