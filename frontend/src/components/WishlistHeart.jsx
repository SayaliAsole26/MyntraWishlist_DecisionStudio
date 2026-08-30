import { useState } from "react";

export default function WishlistHeart({
  productId,
  saved = false,
  onToggle,
  className = "",
  label = "Add to Wishlist",
}) {
  const [busy, setBusy] = useState(false);

  const handleClick = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (busy || !onToggle) return;
    setBusy(true);
    try {
      await onToggle(productId);
    } finally {
      setBusy(false);
    }
  };

  return (
    <button
      type="button"
      className={`wishlist-heart ${saved ? "wishlist-heart--saved" : ""} ${className}`.trim()}
      onClick={handleClick}
      disabled={busy}
      aria-label={saved ? "Remove from Wishlist" : label}
      aria-pressed={saved}
      title={saved ? "Saved to Wishlist" : label}
    >
      <span className="wishlist-heart-icon" aria-hidden>
        {saved ? "♥" : "♡"}
      </span>
    </button>
  );
}
