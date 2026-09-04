import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client.js";
import CompareDrawer from "../components/CompareDrawer.jsx";
import DecisionOverloadModal from "../components/DecisionOverloadModal.jsx";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingState from "../components/LoadingState.jsx";
import PriceInsight from "../components/PriceInsight.jsx";
import QuestionSheet from "../components/QuestionSheet.jsx";
import ReviewInsight from "../components/ReviewInsight.jsx";
import WishlistAlerts from "../components/WishlistAlerts.jsx";
import WishlistCard from "../components/WishlistCard.jsx";
import { useBagIds } from "../hooks/useBagIds.js";
import { compareOptionsFromContext, getDecisionContext } from "../lib/decisionContext.js";
import { useToast } from "../state/ToastContext.jsx";

const MAX_COMPARE = 3;
const OCCASION_ORDER = [
  "Casual",
  "Office",
  "Sports",
  "Vacation",
  "Party",
  "Festive",
  "Everyday",
  "General",
];

function groupByOccasion(items) {
  const map = new Map();
  for (const item of items) {
    const occasion = item.occasion || "General";
    if (!map.has(occasion)) map.set(occasion, []);
    map.get(occasion).push(item);
  }
  const keys = [...map.keys()].sort((a, b) => {
    const ia = OCCASION_ORDER.indexOf(a);
    const ib = OCCASION_ORDER.indexOf(b);
    return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
  });
  return keys.map((occasion) => ({ occasion, items: map.get(occasion) }));
}

export default function Wishlist() {
  const { showToast } = useToast();
  const { has: inBag, add: addToBagId, refresh: refreshBag } = useBagIds();
  const [items, setItems] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [overloads, setOverloads] = useState([]);
  const [overloadClosed, setOverloadClosed] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState([]);

  const [compareOpen, setCompareOpen] = useState(false);
  const [compareResult, setCompareResult] = useState(null);
  const [compareLoading, setCompareLoading] = useState(false);
  const [compareError, setCompareError] = useState("");
  const [shortlistFromCount, setShortlistFromCount] = useState(null);

  const [priceOpen, setPriceOpen] = useState(false);
  const [priceData, setPriceData] = useState(null);
  const [priceLoading, setPriceLoading] = useState(false);
  const [priceError, setPriceError] = useState("");

  const [reviewOpen, setReviewOpen] = useState(false);
  const [reviewData, setReviewData] = useState(null);
  const [reviewLoading, setReviewLoading] = useState(false);
  const [reviewError, setReviewError] = useState("");

  const [questionOpen, setQuestionOpen] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [questionOffset, setQuestionOffset] = useState(0);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [questionLoading, setQuestionLoading] = useState(false);
  const [questionError, setQuestionError] = useState("");
  const [questionAnswer, setQuestionAnswer] = useState(null);
  const [questionProductIds, setQuestionProductIds] = useState([]);

  const cardRefs = useRef({});
  const grouped = useMemo(() => groupByOccasion(items), [items]);

  const load = useCallback(() => {
    setLoading(true);
    Promise.all([api.getWishlist(), refreshBag()])
      .then(([data]) => {
        setItems(data.items);
        setAlerts(data.alerts || []);
        setOverloads(data.overload || []);
        setError("");
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [refreshBag]);

  useEffect(() => {
    load();
  }, [load]);

  const toggleSelect = (productId) => {
    setSelected((prev) => {
      if (prev.includes(productId)) return prev.filter((id) => id !== productId);
      if (prev.length >= MAX_COMPARE) return prev;
      return [...prev, productId];
    });
  };

  const remove = async (productId) => {
    try {
      await api.removeFromWishlist(productId);
      setSelected((prev) => prev.filter((id) => id !== productId));
      load();
    } catch (err) {
      showToast(err.message || "Could not remove item");
    }
  };

  const addToBag = async (productId) => {
    if (inBag(productId)) return;
    try {
      await addToBagId(productId);
    } catch (err) {
      showToast(err.message || "Could not add to bag");
    }
  };

  const dismissAlert = async (alertId) => {
    try {
      await api.dismissAlert(alertId);
      setAlerts((prev) => prev.filter((a) => a.alert_id !== alertId));
    } catch (err) {
      showToast(err.message || "Could not dismiss alert");
    }
  };

  const dismissOverload = () => {
    // Hide for this visit only — popup returns on the next wishlist visit.
    setOverloadClosed(true);
  };

  const viewItem = (productId) => {
    const el = cardRefs.current[productId];
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  };

  const runCompare = async (productIds) => {
    const ids = productIds?.length ? productIds : selected;
    if (ids.length < 2) return;
    setSelected(ids.slice(0, MAX_COMPARE));
    setCompareOpen(true);
    setCompareLoading(true);
    setCompareError("");
    setCompareResult(null);
    try {
      const result = await api.compareWishlist(ids.slice(0, MAX_COMPARE), compareOptionsFromContext());
      setCompareResult(result);
    } catch (err) {
      if (err?.silent || err?.message === "SILENT") return;
      setCompareError(err.message);
    } finally {
      setCompareLoading(false);
    }
  };

  const narrowDown = async (allIds, alertId, groupKey) => {
    setOverloadClosed(true);
    setOverloads((prev) => prev.filter((o) => o.group_key !== groupKey));

    const ctx = getDecisionContext();
    let ids = allIds;
    let fromCount = null;

    setCompareOpen(true);
    setCompareLoading(true);
    setCompareError("");
    setCompareResult(null);
    setSelected([]);

    try {
      if (allIds.length > MAX_COMPARE) {
        try {
          const shortlist = await api.shortlistWishlist(allIds, ctx);
          ids = shortlist.product_ids;
          fromCount = shortlist.from_count;
        } catch {
          ids = allIds.slice(0, MAX_COMPARE);
          fromCount = allIds.length;
        }
      }

      if (ids.length < 2) {
        setCompareError("Need at least 2 items to compare.");
        return;
      }

      setSelected(ids.slice(0, MAX_COMPARE));
      setShortlistFromCount(fromCount);

      const result = await api.compareWishlist(ids.slice(0, MAX_COMPARE), compareOptionsFromContext());
      setCompareResult(result);
      showToast(
        fromCount
          ? `Narrowed ${fromCount} items to 3 — compare ready`
          : "Compare ready for your top picks"
      );

      // Best-effort only — never surface dismiss failures over a successful compare.
      if (alertId) {
        try {
          await api.dismissAlert(alertId);
          setAlerts((prev) => prev.filter((a) => a.alert_id !== alertId));
        } catch {
          /* already dismissed or missing — ignore */
        }
      }
    } catch (err) {
      if (err?.silent || err?.message === "SILENT") {
        /* ignore */
      } else {
        setCompareError(err.message);
      }
    } finally {
      setCompareLoading(false);
    }
  };

  const loadQuestions = useCallback(async (ids, offset = 0) => {
    const data = await api.listQuestions(ids.length || 1, offset);
    setQuestions(data.questions);
  }, []);

  const openQuestions = async (productIds) => {
    const ids = productIds?.length ? productIds : selected;
    setQuestionProductIds(ids);
    setQuestionOpen(true);
    setQuestionAnswer(null);
    setSelectedQuestion(null);
    setQuestionError("");
    setQuestionOffset(0);
    try {
      await loadQuestions(ids, 0);
    } catch (err) {
      setQuestionError(err.message);
    }
  };

  const askAnother = async () => {
    const next = questionOffset + 1;
    setQuestionOffset(next);
    setQuestionAnswer(null);
    setSelectedQuestion(null);
    setQuestionError("");
    try {
      await loadQuestions(questionProductIds, next);
    } catch (err) {
      setQuestionError(err.message);
    }
  };

  const submitQuestion = async () => {
    if (!selectedQuestion) return;
    setQuestionLoading(true);
    setQuestionError("");
    try {
      const body = { question_id: selectedQuestion };
      if (questionProductIds.length >= 2) {
        body.product_ids = questionProductIds;
      } else if (questionProductIds.length === 1) {
        body.product_id = questionProductIds[0];
      } else if (selected.length === 1) {
        body.product_id = selected[0];
      }
      const answer = await api.answerQuestion(body);
      setQuestionAnswer({ ...answer, labels: compareResult?.labels });
    } catch (err) {
      setQuestionError(err.message);
    } finally {
      setQuestionLoading(false);
    }
  };

  const openPriceInsight = async (productId) => {
    setPriceOpen(true);
    setPriceLoading(true);
    setPriceError("");
    setPriceData(null);
    try {
      setPriceData(await api.getPriceInsight(productId));
    } catch (err) {
      setPriceError(err.message);
    } finally {
      setPriceLoading(false);
    }
  };

  const openReviewInsight = async (productId) => {
    setReviewOpen(true);
    setReviewLoading(true);
    setReviewError("");
    setReviewData(null);
    try {
      setReviewData(await api.getReviewInsight(productId));
    } catch (err) {
      setReviewError(err.message);
    } finally {
      setReviewLoading(false);
    }
  };

  return (
    <section className="page wishlist-page">
      <div className="wishlist-header">
        <div>
          <h1>My Wishlist</h1>
          <p className="muted">Items grouped by occasion — compare and decide from here.</p>
        </div>
        <div className="wishlist-header-actions">
          <div className="wishlist-action-bar">
            <button
              type="button"
              className="btn btn-primary btn-sm"
              onClick={() => runCompare()}
              disabled={selected.length < 2}
            >
              Compare my options
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => openQuestions(selected)}
              disabled={selected.length < 1}
            >
              Ask questions
            </button>
            <button
              type="button"
              className="btn btn-clear-selection btn-sm"
              onClick={() => setSelected([])}
              disabled={selected.length === 0}
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      {loading ? <LoadingState message="Loading your Wishlist…" /> : null}
      <ErrorBanner message={!loading ? error : ""} onRetry={load} />

      {!loading ? (
        <WishlistAlerts alerts={alerts} onDismiss={dismissAlert} onViewItem={viewItem} />
      ) : null}

      {!loading && overloads.length > 0 && !overloadClosed ? (
        <DecisionOverloadModal
          overloads={overloads}
          onCompare={(ids, alertId, groupKey) => narrowDown(ids, alertId, groupKey)}
          onDismiss={dismissOverload}
        />
      ) : null}

      {!loading && items.length === 0 ? (
        <EmptyState
          title="Your Wishlist is empty."
          action={
            <Link to="/products" className="btn btn-primary">
              Browse products
            </Link>
          }
        />
      ) : (
        grouped.map(({ occasion, items: groupItems }) => (
          <section key={occasion} className="wishlist-occasion-block">
            <h2 className="wishlist-occasion-title">{occasion}</h2>
            <ul className="wishlist-grid">
              {groupItems.map((item) => (
                <WishlistCard
                  key={item.product_id}
                  ref={(el) => {
                    cardRefs.current[item.product_id] = el;
                  }}
                  item={item}
                  selected={selected.includes(item.product_id)}
                  onToggleSelect={toggleSelect}
                  onRemove={remove}
                  onAddToBag={addToBag}
                  onPriceInsight={openPriceInsight}
                  onReviewInsight={openReviewInsight}
                  inBag={inBag(item.product_id)}
                />
              ))}
            </ul>
          </section>
        ))
      )}

      <CompareDrawer
        open={compareOpen}
        onClose={() => {
          setCompareOpen(false);
          setShortlistFromCount(null);
        }}
        result={compareResult}
        loading={compareLoading}
        error={compareError}
        fromCount={shortlistFromCount}
      />

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
        onAddRecommended={addToBag}
      />

      <PriceInsight
        open={priceOpen}
        onClose={() => setPriceOpen(false)}
        data={priceData}
        loading={priceLoading}
        error={priceError}
      />

      <ReviewInsight
        open={reviewOpen}
        onClose={() => setReviewOpen(false)}
        data={reviewData}
        loading={reviewLoading}
        error={reviewError}
      />
    </section>
  );
}
