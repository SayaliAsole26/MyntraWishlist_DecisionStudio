import {
  CONFIDENCE_LABELS,
  NEED_OPTIONS,
  TRADEOFF_OPTIONS,
} from "../lib/decisionContext.js";

export default function DecisionStudioSetup({ context, onChange }) {
  const confidenceLabel = CONFIDENCE_LABELS[context.confidence] ?? CONFIDENCE_LABELS[2];

  return (
    <div className="decision-setup">
      <section className="decision-setup-step">
        <p className="decision-step-label">
          <span className="decision-step-num">01</span> Define the need
        </p>
        <h2 className="decision-step-title">What are you choosing?</h2>
        <div className="decision-chip-row" role="group" aria-label="Shopping need">
          {NEED_OPTIONS.map((opt) => (
            <button
              key={opt.id}
              type="button"
              className={`decision-chip${context.need === opt.id ? " decision-chip-active" : ""}`}
              aria-pressed={context.need === opt.id}
              onClick={() => onChange({ need: opt.id })}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </section>

      <section className="decision-setup-step">
        <p className="decision-step-label">
          <span className="decision-step-num">02</span> Trade-off — what matters
        </p>
        <h2 className="decision-step-title">Pick your top priority</h2>
        <div className="decision-chip-row" role="group" aria-label="Trade-off priority">
          {TRADEOFF_OPTIONS.map((opt) => (
            <button
              key={opt.id}
              type="button"
              className={`decision-chip${context.tradeoff === opt.id ? " decision-chip-active" : ""}`}
              aria-pressed={context.tradeoff === opt.id}
              onClick={() => onChange({ tradeoff: opt.id })}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </section>

      <section className="decision-setup-step">
        <p className="decision-step-label">
          <span className="decision-step-num">03</span> Confidence check
        </p>
        <h2 className="decision-step-title">How sure are you about this choice?</h2>
        <div className="confidence-slider-wrap">
          <input
            type="range"
            min={0}
            max={4}
            step={1}
            value={context.confidence}
            className="confidence-slider"
            aria-valuetext={confidenceLabel}
            onChange={(e) => onChange({ confidence: Number(e.target.value) })}
          />
          <div className="confidence-slider-labels">
            <span>Not sure</span>
            <span className="confidence-current">{confidenceLabel}</span>
            <span>Very sure</span>
          </div>
        </div>
      </section>
    </div>
  );
}
