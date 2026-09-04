import { friendlyError } from "../lib/friendlyError.js";

// Production uses same-origin paths so Vercel proxies to Railway (works on Wi‑Fi + mobile data).
// Locally, empty VITE_API_URL uses the Vite dev proxy to port 8002.
const configured = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");
const forceDirect = import.meta.env.VITE_FORCE_DIRECT_API === "true";
const API =
  import.meta.env.PROD && !forceDirect ? "" : configured;
const USER_ID = "U001";

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(`${API}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        "X-User-Id": USER_ID,
        ...options.headers,
      },
    });
  } catch {
    throw new Error("Connection issue. Please try again.");
  }
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = typeof data.detail === "string" ? data.detail : null;
    const msg = friendlyError(detail || `HTTP ${res.status}`);
    if (!msg) {
      // Silent / non-user-facing failures (e.g. already-dismissed alert)
      const silent = new Error("SILENT");
      silent.silent = true;
      throw silent;
    }
    throw new Error(msg);
  }
  return data;
}

export const api = {
  getHealth: () => request("/health"),
  getCategories: () => request("/api/products/categories/list"),
  getProducts: (category) =>
    request(category ? `/api/products?category=${encodeURIComponent(category)}` : "/api/products"),
  getProduct: (id) => request(`/api/products/${id}`),
  getWishlist: () => request("/api/wishlist"),
  compareWishlist: (productIds, options = {}) =>
    request("/api/wishlist/compare", {
      method: "POST",
      body: JSON.stringify({
        product_ids: productIds,
        need: options.need ?? null,
        tradeoff_priority: options.tradeoff_priority ?? null,
        user_confidence: options.user_confidence ?? null,
      }),
    }),
  shortlistWishlist: (productIds, options = {}) =>
    request("/api/wishlist/shortlist", {
      method: "POST",
      body: JSON.stringify({
        product_ids: productIds,
        need: options.need ?? null,
        tradeoff_priority: options.tradeoff_priority ?? null,
      }),
    }),
  getPriceInsight: (productId) => request(`/api/products/${productId}/price-insight`),
  getReviewInsight: (productId) => request(`/api/products/${productId}/review-insight`),
  listQuestions: (productCount = 1, offset = 0) =>
    request(`/api/questions?product_count=${productCount}&offset=${offset}`),
  answerQuestion: (body) =>
    request("/api/questions/answer", { method: "POST", body: JSON.stringify(body) }),
  addToWishlist: (productId, occasion = "General", size = null) =>
    request("/api/wishlist", {
      method: "POST",
      body: JSON.stringify({ product_id: productId, occasion, size }),
    }),
  dismissAlert: (alertId) =>
    request(`/api/alerts/${alertId}/dismiss`, { method: "PATCH" }),
  removeFromWishlist: (productId) =>
    request(`/api/wishlist/${productId}`, { method: "DELETE" }),
  getBag: () => request("/api/bag"),
  addToBag: (productId) =>
    request("/api/bag", { method: "POST", body: JSON.stringify({ product_id: productId }) }),
  removeFromBag: (productId) =>
    request(`/api/bag/${productId}`, { method: "DELETE" }),
  checkout: () => request("/api/checkout", { method: "POST" }),
  getProfile: () => request("/api/profile"),
  updateProfile: (body) =>
    request("/api/profile", { method: "PATCH", body: JSON.stringify(body) }),
  clearProfile: () => request("/api/profile/clear", { method: "POST" }),
};

export function formatPrice(amount) {
  return `₹${amount.toLocaleString("en-IN")}`;
}
