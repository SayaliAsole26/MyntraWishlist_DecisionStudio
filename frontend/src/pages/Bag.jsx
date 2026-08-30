import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, formatPrice } from "../api/client.js";
import ProductImage from "../components/ProductImage.jsx";
import CheckoutConfirmation from "../components/CheckoutConfirmation.jsx";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingState from "../components/LoadingState.jsx";

export default function Bag() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [checkingOut, setCheckingOut] = useState(false);
  const [order, setOrder] = useState(null);

  const load = () => {
    setLoading(true);
    api
      .getBag()
      .then((data) => {
        setItems(data.items);
        setTotal(data.total);
        setError("");
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const remove = async (productId) => {
    try {
      await api.removeFromBag(productId);
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  const checkout = async () => {
    if (items.length === 0) return;
    setCheckingOut(true);
    setError("");
    try {
      const result = await api.checkout();
      setOrder(result);
      setItems([]);
      setTotal(0);
    } catch (err) {
      setError(err.message);
    } finally {
      setCheckingOut(false);
    }
  };

  return (
    <section className="page bag-page">
      <h1>Bag</h1>
      <p className="muted lede">Review items and finish with mock checkout — no payment gateway.</p>

      {loading ? <LoadingState message="Loading your bag…" /> : null}
      <ErrorBanner message={!loading ? error : ""} onRetry={load} />

      {!loading && items.length === 0 && !order ? (
        <EmptyState
          title="Your bag is empty."
          action={
            <Link to="/products" className="btn btn-primary">
              Continue shopping
            </Link>
          }
        />
      ) : null}

      {!loading && items.length > 0 ? (
        <>
          <ul className="line-list">
            {items.map((item) => (
              <li key={item.product_id} className="line-item">
                <Link to={`/product/${item.product_id}`} className="line-thumb">
                  <ProductImage src={item.product.image_url} alt={item.product.name} />
                </Link>
                <div className="line-body">
                  <p className="product-brand">{item.product.brand}</p>
                  <Link to={`/product/${item.product_id}`} className="line-title">
                    {item.product.name}
                  </Link>
                  <p className="product-price">
                    {formatPrice(item.product.price)}
                    {item.quantity > 1 ? <span className="muted"> × {item.quantity}</span> : null}
                  </p>
                </div>
                <button type="button" className="btn btn-ghost btn-sm" onClick={() => remove(item.product_id)}>
                  Remove
                </button>
              </li>
            ))}
          </ul>
          <div className="bag-footer">
            <p className="bag-total">
              Total <strong>{formatPrice(total)}</strong>
            </p>
            <button type="button" className="btn btn-primary" onClick={checkout} disabled={checkingOut}>
              {checkingOut ? "Placing order…" : "Place order"}
            </button>
          </div>
        </>
      ) : null}

      <CheckoutConfirmation order={order} onClose={() => setOrder(null)} />
    </section>
  );
}
