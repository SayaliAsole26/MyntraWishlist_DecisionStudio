import PriceAlert from "./PriceAlert.jsx";

export default function WishlistAlerts({ alerts, onDismiss, onViewItem }) {
  const priceAlerts = alerts?.filter((a) => a.type === "PRICE_DROP") || [];
  if (!priceAlerts.length) return null;

  return (
    <div className="wishlist-alerts">
      {priceAlerts.map((alert) => (
        <PriceAlert
          key={alert.alert_id}
          alert={alert}
          onDismiss={onDismiss}
          onViewItem={onViewItem}
        />
      ))}
    </div>
  );
}
