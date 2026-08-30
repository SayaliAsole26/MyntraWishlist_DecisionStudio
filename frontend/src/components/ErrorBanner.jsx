export default function ErrorBanner({ message, onRetry }) {
  if (!message) return null;

  return (
    <div className="error-banner" role="alert">
      <p>{message}</p>
      {onRetry ? (
        <button type="button" className="btn btn-ghost btn-sm error-retry" onClick={onRetry}>
          Try again
        </button>
      ) : null}
    </div>
  );
}
