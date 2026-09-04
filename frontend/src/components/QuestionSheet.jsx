export default function QuestionSheet({
  open,
  onClose,
  questions,
  selectedId,
  onSelect,
  onSubmit,
  loading,
  answer,
  error,
  onAddRecommended,
}) {
  if (!open) return null;

  const recommendedId =
    answer?.recommended_product_id ||
    (answer?.recommendation && answer?.labels?.best_balance) ||
    null;

  const errText =
    error && !/alert not found|already dismissed|SILENT|HTTP\s*\d/i.test(String(error))
      ? error
      : null;

  return (
    <div className="sheet-backdrop" onClick={onClose} role="presentation">
      <div
        className="sheet question-sheet sheet-enter"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-label="Ask a question"
      >
        <div className="sheet-header">
          <h2>Ask a question</h2>
          <button type="button" className="btn btn-ghost btn-sm" onClick={onClose}>
            Close
          </button>
        </div>

        <div className="sheet-body">
          {!answer ? (
            <>
              <p className="muted small">Pick a predefined question — no free-text chat.</p>
              <fieldset className="question-options">
                {questions.map((q) => (
                  <label key={q.question_id} className="question-option">
                    <input
                      type="radio"
                      name="question"
                      value={q.question_id}
                      checked={selectedId === q.question_id}
                      onChange={() => onSelect(q.question_id)}
                    />
                    <span>{q.label}</span>
                  </label>
                ))}
              </fieldset>
              <button
                type="button"
                className="btn btn-primary"
                disabled={!selectedId || loading}
                onClick={onSubmit}
              >
                {loading ? "Thinking…" : "Get answer"}
              </button>
              {errText ? <p className="error-banner">{errText}</p> : null}
            </>
          ) : (
            <div className="answer-card">
              <p className="answer-headline">{answer.answer || "Answer"}</p>
              <p className="muted small">Confidence: {answer.confidence}</p>

              {answer.facts?.length ? (
                <section className="answer-section">
                  <h3>Facts</h3>
                  <ul>
                    {answer.facts.map((f) => (
                      <li key={f}>{f}</li>
                    ))}
                  </ul>
                </section>
              ) : null}

              {answer.evidence?.length ? (
                <section className="answer-section">
                  <h3>Evidence</h3>
                  <ul>
                    {answer.evidence.map((e) => (
                      <li key={e}>{e}</li>
                    ))}
                  </ul>
                </section>
              ) : null}

              {answer.interpretation ? (
                <section className="answer-section">
                  <h3>Interpretation</h3>
                  <p>{answer.interpretation}</p>
                </section>
              ) : null}

              {answer.recommendation ? (
                <section className="answer-section">
                  <h3>Recommendation</h3>
                  <p>{answer.recommendation}</p>
                </section>
              ) : null}

              <div className="answer-actions">
                <button
                  type="button"
                  className="btn btn-primary ask-another-btn"
                  onClick={() => onSelect(null)}
                >
                  Ask another question
                </button>
                {onAddRecommended && answer.labels?.best_balance ? (
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={() => onAddRecommended(answer.labels.best_balance)}
                  >
                    Add {answer.labels.best_balance} to Bag
                  </button>
                ) : null}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
