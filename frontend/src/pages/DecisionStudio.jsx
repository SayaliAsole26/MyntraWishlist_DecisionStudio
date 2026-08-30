import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, formatPrice } from "../api/client.js";
import ComparisonTable from "../components/ComparisonTable.jsx";
import DecisionStudioSetup from "../components/DecisionStudioSetup.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingState from "../components/LoadingState.jsx";
import QuestionSheet from "../components/QuestionSheet.jsx";
import { useBagIds } from "../hooks/useBagIds.js";
import { useDecisionContext } from "../hooks/useDecisionContext.js";
import { useToast } from "../state/ToastContext.jsx";

const INSIGHT_UNAVAILABLE_PREFIX = "Decision insight temporarily unavailable";

function productLabel(products, productId) {
  const product = products?.find((p) => p.product_id === productId);
  return product ? `${product.brand} ${product.name}` : productId;
}

export default function DecisionStudio() {
  const { showToast } = useToast();
  const { has: inBag, add: addToBag, refresh: refreshBag } = useBagIds();
  const { context, setContext, compareOptions } = useDecisionContext();
  const [searchParams] = useSearchParams();
  const idsParam = searchParams.get("ids") || "";
  const fromCount = searchParams.get("from");
  const productIds = idsParam.split(",").filter(Boolean).slice(0, 3);

  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const [questionOpen, setQuestionOpen] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [questionOffset, setQuestionOffset] = useState(0);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [questionLoading, setQuestionLoading] = useState(false);
  const [questionError, setQuestionError] = useState("");
  const [questionAnswer, setQuestionAnswer] = useState(null);
  const [addingTopPick, setAddingTopPick] = useState(false);

  const loadCompare = useCallback(() => {
    if (productIds.length < 2) {
      setLoading(false);
      setError("Select at least 2 Wishlist items to analyse.");
      return;
    }
    setLoading(true);
    setError("");
    api
      .compareWishlist(productIds, compareOptions())
      .then(setResult)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [idsParam, context.need, context.tradeoff, context.confidence]);

  useEffect(() => {
    loadCompare();
    refreshBag();
  }, [loadCompare, refreshBag]);

  const handleContextChange = (partial) => {
    setContext(partial);
  };

  const loadQuestions = useCallback(
    (offset = 0) => {
      return api.listQuestions(productIds.length, offset).then((data) => {
        setQuestions(data.questions);
      });
    },
    [productIds.length]
  );

  const openQuestions = async () => {
    setQuestionOpen(true);
    setQuestionAnswer(null);
    setSelectedQuestion(null);
    setQuestionError("");
    try {
      await loadQuestions(questionOffset);
    } catch (err) {
      setQuestionError(err.message);
    }
  };

  const submitQuestion = async () => {
    if (!selectedQuestion) return;
    setQuestionLoading(true);
    setQuestionError("");
    try {
      const answer = await api.answerQuestion({
        question_id: selectedQuestion,
        product_ids: productIds,
      });
      setQuestionAnswer({ ...answer, labels: result?.labels });
    } catch (err) {
      setQuestionError(err.message);
    } finally {
      setQuestionLoading(false);
    }
  };

  const askAnother = async () => {
    const next = questionOffset + 1;
    setQuestionOffset(next);
    setQuestionAnswer(null);
    setSelectedQuestion(null);
    setQuestionError("");
    try {
      await loadQuestions(next);
    } catch (err) {
      setQuestionError(err.message);
    }
  };

  const bestId = result?.labels?.best_balance;
  const bestProduct = result?.products?.find((p) => p.product_id === bestId);
  const topPickNeedFit = result?.top_pick_need_fit;
  const needAssessment = result?.need_assessment || {};
  const topPickInBag = bestId ? inBag(bestId) : false;

  const insightTradeoffs = useMemo(() => {
    if (!result?.explanation?.tradeoffs?.length) return [];
    return result.explanation.tradeoffs.filter(
      (item) => item && !item.startsWith(INSIGHT_UNAVAILABLE_PREFIX)
    );
  }, [result]);

  const extraInsightText = useMemo(() => {
    const text = result?.explanation?.text?.trim();
    if (!text || text.startsWith(INSIGHT_UNAVAILABLE_PREFIX) || text === result?.summary) {
      return null;
    }
    return text;
  }, [result]);

  const addTopPickToBag = async () => {
    if (!bestId || topPickInBag) return;
    setAddingTopPick(true);
    try {
      await addToBag(bestId);
      showToast("Added to Bag");
    } catch (err) {
      showToast(err.message);
    } finally {
      setAddingTopPick(false);
    }
  };

  return (
    <section className="page decision-studio-page">
      <div className="section-head">
        <div>
          <h1>Decision Studio</h1>
          <p className="muted">Detailed comparison and grounded answers for your shortlist.</p>
        </div>
        <Link to="/wishlist" className="text-link">
          Back to Wishlist
        </Link>
      </div>

      <DecisionStudioSetup context={context} onChange={handleContextChange} />

      {fromCount ? (
        <p className="shortlist-note">
          Automatically narrowed <strong>{fromCount}</strong> similar saves to{" "}
          <strong>3</strong> most relevant for your need.
        </p>
      ) : null}

      {loading ? <LoadingState message="Loading analysis…" /> : null}
      <ErrorBanner message={!loading ? error : ""} onRetry={loadCompare} />

      {!loading && result ? (
        <div className="decision-studio-body">
          {bestProduct ? (
            <div className="top-pick-block">
              <p className="compare-pick">
                Top pick: <strong>{bestProduct.brand}</strong> — {bestProduct.name} (
                {formatPrice(bestProduct.price)})
              </p>
              {topPickNeedFit?.level === "partial" || topPickNeedFit?.level === "poor" ? (
                <p className="need-fit-warning" role="status">
                  {topPickNeedFit.reason}
                </p>
              ) : topPickNeedFit?.level === "strong" && context.need ? (
                <p className="need-fit-ok muted small">{topPickNeedFit.reason}</p>
              ) : null}
              <button
                type="button"
                className={topPickInBag ? "btn btn-added" : "btn btn-primary"}
                onClick={addTopPickToBag}
                disabled={topPickInBag || addingTopPick}
              >
                {topPickInBag ? "Added to Bag" : addingTopPick ? "Adding…" : "Add top pick to Bag"}
              </button>
            </div>
          ) : null}

          {Object.keys(needAssessment).length > 0 && context.need ? (
            <div className="need-assessment-block">
              <h3>Need fit by item</h3>
              <ul className="need-assessment-list">
                {result.products.map((p) => {
                  const fit = needAssessment[p.product_id];
                  if (!fit) return null;
                  return (
                    <li
                      key={p.product_id}
                      className={`need-assessment-item need-assessment-${fit.level}`}
                    >
                      <strong>
                        {p.brand} {p.name}
                      </strong>
                      <span>{fit.reason}</span>
                    </li>
                  );
                })}
              </ul>
            </div>
          ) : null}

          <div className="compare-explanation decision-insight-block">
            <h3>Decision insight</h3>
            {result.summary ? <p className="compare-summary">{result.summary}</p> : null}
            {result.labels ? (
              <div className="label-row">
                <span className="label-chip">
                  Best value: {productLabel(result.products, result.labels.best_value)}
                </span>
                <span className="label-chip">
                  Best reviewed: {productLabel(result.products, result.labels.best_reviewed)}
                </span>
                <span className="label-chip">
                  Best balance: {productLabel(result.products, result.labels.best_balance)}
                </span>
              </div>
            ) : null}
            {extraInsightText ? <p className="decision-insight-extra">{extraInsightText}</p> : null}
            {insightTradeoffs.length ? (
              <ul className="decision-insight-tradeoffs">
                {insightTradeoffs.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : null}
          </div>

          <ComparisonTable rows={result.rows} products={result.products} labels={result.labels} />

          <div className="decision-studio-actions">
            <button type="button" className="btn btn-secondary" onClick={openQuestions}>
              Ask a question
            </button>
          </div>
        </div>
      ) : null}

      <QuestionSheet
        open={questionOpen}
        onClose={() => setQuestionOpen(false)}
        questions={questions}
        selectedId={selectedQuestion}
        onSelect={(id) => {
          if (id === null) {
            askAnother();
            return;
          }
          setSelectedQuestion(id);
          setQuestionAnswer(null);
        }}
        onSubmit={submitQuestion}
        loading={questionLoading}
        answer={questionAnswer}
        error={questionError}
      />
    </section>
  );
}
