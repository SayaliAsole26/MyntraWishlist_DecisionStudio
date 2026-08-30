import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client.js";

export function useWishlistIds() {
  const [ids, setIds] = useState(new Set());
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(() => {
    return api
      .getWishlist()
      .then((data) => {
        setIds(new Set(data.items.map((i) => i.product_id)));
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const add = useCallback(async (productId) => {
    await api.addToWishlist(productId);
    setIds((prev) => new Set(prev).add(productId));
  }, []);

  const remove = useCallback(async (productId) => {
    await api.removeFromWishlist(productId);
    setIds((prev) => {
      const next = new Set(prev);
      next.delete(productId);
      return next;
    });
  }, []);

  const toggle = useCallback(
    async (productId) => {
      if (ids.has(productId)) {
        await remove(productId);
        return false;
      }
      await add(productId);
      return true;
    },
    [ids, add, remove]
  );

  return { ids, loading, add, remove, toggle, refresh };
}
