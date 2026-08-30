import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client.js";

export function useBagIds() {
  const [ids, setIds] = useState(new Set());
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(() => {
    return api
      .getBag()
      .then((data) => {
        setIds(new Set(data.items.map((i) => i.product_id)));
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const add = useCallback(async (productId) => {
    await api.addToBag(productId);
    setIds((prev) => new Set(prev).add(productId));
  }, []);

  return { ids, loading, add, refresh, has: (productId) => ids.has(productId) };
}
