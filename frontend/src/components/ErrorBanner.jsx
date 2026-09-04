import { friendlyError } from "../lib/friendlyError.js";

export default function ErrorBanner({ message, onRetry }) {
  const text = friendlyError(message, null);
  if (!text) return null;

  return (
    <div className="error-banner" role="alert">
      <p>{text}</p>
      {onRetry ? (
        <button type="button" className="btn btn-ghost btn-sm error-retry" onClick={onRetry}>
          Try again
        </button>
      ) : null}
    </div>
  );
}
