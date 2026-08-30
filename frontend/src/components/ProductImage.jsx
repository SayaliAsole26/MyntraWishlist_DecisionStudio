import { useState } from "react";

const FALLBACK =
  "data:image/svg+xml," +
  encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="500" viewBox="0 0 400 500"><rect fill="#f5f5f6" width="400" height="500"/><text x="200" y="250" text-anchor="middle" fill="#94969f" font-family="sans-serif" font-size="16">Image unavailable</text></svg>'
  );

export default function ProductImage({ src, alt, className, loading = "lazy" }) {
  const [failed, setFailed] = useState(false);

  return (
    <img
      src={failed || !src ? FALLBACK : src}
      alt={alt}
      className={className}
      loading={loading}
      onError={() => setFailed(true)}
    />
  );
}
