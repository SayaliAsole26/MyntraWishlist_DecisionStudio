import WishlistOccasionModal from "./WishlistOccasionModal.jsx";
import WishlistSizeModal from "./WishlistSizeModal.jsx";

export default function WishlistAddModals({ addStep, pendingProduct, onConfirmSize, onConfirmOccasion, onCancel }) {
  return (
    <>
      <WishlistSizeModal
        open={addStep === "size"}
        product={pendingProduct}
        onConfirm={onConfirmSize}
        onCancel={onCancel}
      />
      <WishlistOccasionModal
        open={addStep === "occasion"}
        onConfirm={onConfirmOccasion}
        onCancel={onCancel}
      />
    </>
  );
}
