# MYNTRA WISHLIST DECISION STUDIO
## Problem Statement

This document defines the problem the MVP exists to solve. It is derived from `Docs/Context.md.md` and should be read as the product-problem layer: why the work matters, who is affected, and what a successful resolution looks like.

Implementation locks: `Docs/Doc_Alignment.md`. Build order: `Docs/Phase_wise_Implementation.md`.

---

## 1. One-Line Problem

Users save products to Wishlist because they are interested, but saving does not resolve the uncertainty that stops them from buying. Wishlist remains a passive collection instead of a place to decide.

---

## 2. The Core Problem

Fashion shoppers browse, shortlist, and save on a Myntra-like store ([https://www.myntra.com/](https://www.myntra.com/) as visual reference only). They often leave with **saved intent**, not a **resolved purchase decision**.

A Wishlist item is not a committed buy. It is often a postponement caused by unanswered questions:

- Whether the product is worth the current price
- Which shortlisted product is actually better
- Whether quality is reliable
- Whether fit or size will work
- What existing buyers liked or disliked
- Whether a better alternative already exists
- Whether the current price is attractive relative to history
- Whether they should buy now or wait
- Which product best matches their personal priorities

**The gap:** Myntra-like shopping helps users discover and save. It does not help them decide among what they have already saved.

---

## 3. Who Has This Problem

**Primary user:** A fashion shopper who has already shown interest by adding products to Wishlist, but is not yet ready to add to Bag.

Typical situation:

- Multiple similar items saved (for example, 3–5 dresses, sneakers, or tops)
- Mixed signals on price, ratings, fit, fabric, and value
- No clear way to compare trade-offs without leaving Wishlist
- No trusted, evidence-based answer to “which one should I buy?”

**Business stakeholder:** The commerce platform, which sees Wishlist as a high-intent surface that currently under-converts to Bag and purchase.

---

## 4. Current State

Today, Wishlist typically shows:

- Product image
- Product name
- Price
- Heart / saved state

That is enough to **remember** a product. It is not enough to **resolve** a purchase.

What is missing on the Wishlist surface:

| User need | Current Wishlist |
|---|---|
| Compare 2–3 saved items | Leave Wishlist or compare mentally |
| Understand price quality (vs MRP, vs history, vs saved price) | Price is shown; price *decision* is not |
| Know what buyers actually like or dislike | Rating number only; no review themes |
| Ask a specific purchase question | No structured Q&A on the saved item |
| Spot a better similar option | No similarity or alternative signal |
| Handle too many similar saves | Overload is invisible |
| Act on a price drop | No contextual price-drop cue |
| Get an explainable recommendation | No evidence-based “best match for you” |

The shopper must reconstruct the decision themselves: open product pages, scroll reviews, remember prices, and guess which item fits their priorities.

---

## 5. Why This Matters

### User cost

Unresolved uncertainty produces:

- Abandoned intent
- Decision fatigue when many similar items are saved
- Low-confidence purchases, or no purchase at all
- Repeated browsing instead of closing the loop

The emotional state is:

> “I like these products, but I don’t know which one to buy.”

Not:

> “I need a new shopping app.”

### Business cost

Saved products are a strong signal of interest. If that signal is not converted, the platform loses:

```
Wishlist additions
    ↓
Unresolved decisions
    ↓
Weak Wishlist-to-Bag conversion
    ↓
Weak Wishlist-to-Purchase conversion
```

The business goal this problem blocks:

> Increase the percentage of users who purchase at least one item from their Wishlist within 30 days of adding it.

---

## 6. What Is Not the Problem

This is **not** a request to recreate the entire Myntra application.

The following are **not** the problems this MVP is trying to solve:

- Discovery volume (more browsing, more categories, more catalog)
- More Wishlist additions as a success metric
- Longer sessions or more AI interactions for their own sake
- Building a ChatGPT-like shopping assistant
- Building a research tool, analytics dashboard, or separate “Decision Studio” product
- Production payments, full auth, live inventory, seller ops, or catalog-scale ML

Optimizing for more saves, more chat, or more pages would **worsen** the real problem: users already have too many unresolved options.

---

## 7. Desired Future State

Wishlist should become an **active decision workspace** embedded in the shopping experience.

The intended journey:

```
SAVED INTENT
    ↓
WISHLIST
    ↓
IDENTIFY UNCERTAINTY
    ↓
EVIDENCE / COMPARISON / ANSWERS
    ↓
DECISION RESOLVED
    ↓
ADD TO BAG
    ↓
PURCHASE
```

The user should feel:

> “I already saved these products because I am interested in them. Now Myntra is helping me decide.”

The user should **not** feel they have entered a separate AI application.

Product principle:

> Don’t help users save more products. Help them confidently resolve which saved product is right for them.

Success is a shift from:

> “I like these products but I don’t know which one to buy”

to:

> “I understand the trade-offs and know which one is right for me.”

---

## 8. Problem Dimensions the Product Must Address

These are the uncertainties that currently stall purchase. The MVP must reduce them **inside Wishlist**, without manufacturing confidence.

| Dimension | Unanswered question |
|---|---|
| Choice | Which one should I buy? |
| Value | Is this worth the price? |
| Social proof | What do buyers dislike? |
| Quality | Is quality reliable? |
| Fit | Is the fit reliable? |
| Alternatives | Is there a better option in my Wishlist? |
| Timing | Should I buy now or wait for a better price? |
| Relevance | Why this over another product, given my priorities? |
| Overload | I have saved too many similar products — help me narrow down. |

Reducing these uncertainties must not add unnecessary friction. Weak evidence must be stated as weak evidence, not as certainty.

---

## 9. Constraints That Shape the Solution

These constraints are part of the problem definition: the wrong kind of solution would fail even if “AI” were added.

1. **No separate Decision Studio page.** Comparison, price analysis, review intelligence, Q&A, alerts, and recommendations must happen contextually in Wishlist.
2. **AI is a layer, not the product.** The experience must still feel like fashion commerce: product imagery, familiar shopping patterns, mobile-friendly actions.
3. **Do not invent evidence.** Missing reviews, prices, or history must be disclosed. Interpretation must not be presented as fact.
4. **Questions are structured, not open chat.** The core job is resolving a decision about saved products, not answering anything about shopping.
5. **Recommendations must be explainable and conditional.** Trade-offs over undeclared winners. Preference-weighted, not “definitely the best.”
6. **Smallest convincing end-to-end experience.** Demonstrate the funnel: save → decide → bag → mock purchase. Do not build catalog-scale infrastructure first.

---

## 10. How We Will Know the Problem Is Addressed

The MVP does not need production analytics. The experience must still make the conversion funnel *demonstrable*.

A user should be able to:

1. Browse and save products that create real choice conflict
2. Open Wishlist and see decision signals, not only a saved list
3. Compare 2–3 items and understand trade-offs (value, reviews, fit, quality)
4. Inspect price in context (current, MRP, saved price, historical range) without false future-price claims
5. See review themes (likes and concerns), not only a sentiment percentage
6. Ask a predefined purchase question and get an evidence-grounded answer
7. Be prompted when similar items pile up, when a similar alternative exists, or when price drops
8. Receive a preference-aware recommendation that explains *why* and *what is traded off*
9. Add the chosen product to Bag and complete a mock checkout

**Demo story that proves the problem is solved:** save several similar products → system surfaces overload → compare → ask “which one should I buy?” → see trade-offs and price insight → decide → add to Bag.

---

## 11. Success Definition

| Layer | Success |
|---|---|
| **User** | Genuine purchase uncertainty is reduced. The shopper can choose among saved items with understandable evidence. |
| **Product** | Wishlist functions as a decision workspace. No parallel AI destination is required. |
| **Business (conceptual)** | More resolved decisions from existing Wishlist intent, visible as Wishlist → Bag → purchase. |
| **Integrity** | Confidence tracks evidence strength. Gaps are explicit. No fabricated specs, reviews, ratings, or prices. |

The MVP succeeds when Wishlist stops being a parking lot for products and starts being the place where saved intent becomes a quality purchase decision.
