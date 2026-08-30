import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client.js";

export function useWishlistAdd(showToast) {
  const [ids, setIds] = useState(new Set());
  const [pendingProduct, setPendingProduct] = useState(null);
  const [pendingSize, setPendingSize] = useState(null);
  const [addStep, setAddStep] = useState(null);
  const [loading, setLoading] = useState(true);

  const resetPending = useCallback(() => {
    setPendingProduct(null);
    setPendingSize(null);
    setAddStep(null);
  }, []);

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

  const remove = useCallback(
    async (productId) => {
      await api.removeFromWishlist(productId);
      setIds((prev) => {
        const next = new Set(prev);
        next.delete(productId);
        return next;
      });
      showToast?.("Removed from Wishlist");
      return false;
    },
    [showToast]
  );

  const confirmSize = useCallback((size) => {
    setPendingSize(size);
    setAddStep("occasion");
  }, []);

  const confirmAdd = useCallback(
    async (occasion) => {
      if (!pendingProduct) return false;
      await api.addToWishlist(pendingProduct.product_id, occasion, pendingSize);
      setIds((prev) => new Set(prev).add(pendingProduct.product_id));
      resetPending();
      showToast?.(
        pendingSize
          ? `Added size ${pendingSize} to Wishlist`
          : "Added to Wishlist"
      );
      return true;
    },
    [pendingProduct, pendingSize, resetPending, showToast]
  );

  const cancelAdd = useCallback(() => {
    resetPending();
  }, [resetPending]);

  const startAddFlow = useCallback((product) => {
    setPendingProduct(product);
    setPendingSize(null);
    if (product.sizes?.length) {
      setAddStep("size");
    } else {
      setAddStep("occasion");
    }
  }, []);

  const handleToggle = useCallback(
    async (productOrId, productHint) => {
      let product = productHint;
      const productId =
        typeof productOrId === "string" ? productOrId : productOrId?.product_id;

      if (!productId) return null;

      if (ids.has(productId)) {
        return remove(productId);
      }

      if (!product && typeof productOrId === "object") {
        product = productOrId;
      }
      if (!product) {
        try {
          product = await api.getProduct(productId);
        } catch {
          showToast?.("Could not load product details");
          return null;
        }
      }

      startAddFlow(product);
      return null;
    },
    [ids, remove, showToast, startAddFlow]
  );

  return {
    ids,
    loading,
    addStep,
    pendingProduct,
    handleToggle,
    confirmSize,
    confirmAdd,
    cancelAdd,
    refresh,
  };
}
