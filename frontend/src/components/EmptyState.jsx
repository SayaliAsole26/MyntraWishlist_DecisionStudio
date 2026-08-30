export default function EmptyState({ title, action }) {
  return (
    <div className="empty-state">
      <p>{title}</p>
      {action}
    </div>
  );
}
