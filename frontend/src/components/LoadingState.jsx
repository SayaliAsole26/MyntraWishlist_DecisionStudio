export default function LoadingState({ message = "Loading…" }) {
  return (
    <div className="loading-state" role="status">
      <span className="loading-spinner" aria-hidden />
      <p className="muted">{message}</p>
    </div>
  );
}
