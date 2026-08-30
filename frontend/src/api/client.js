const API = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");
const USER_ID = "U001";

function apiReachabilityHint() {
  if (!API) {
    return "Start the backend: uvicorn backend.main:app --reload --host 127.0.0.1 --port 8002";
  }
  return [
    "Check: (1) VITE_API_URL on Vercel matches your Railway domain (no trailing slash),",
    "(2) Railway CORS_ORIGINS includes this site's URL,",
    "(3) your network resolves *.up.railway.app (try Google DNS 8.8.8.8 if needed).",
  ].join(" ");
}

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
    throw new Error(`Cannot reach API at ${API || "same origin"}. ${apiReachabilityHint()}`);
  }
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || `HTTP ${res.status}`);
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
