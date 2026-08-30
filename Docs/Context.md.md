# MYNTRA WISHLIST DECISION STUDIO
## Project Context & Product Requirements

This document is the persistent context for the Myntra Wishlist Decision Studio MVP. It should be read before making any architectural changes and should guide all implementation decisions.

---

## 1. Project Overview

We are building a functional MVP inspired by Myntra's fashion-commerce experience.

**Reference storefront (inspiration only — do not scrape, do not depend on live availability):** [https://www.myntra.com/](https://www.myntra.com/)

The purpose of this MVP is **NOT** to recreate the entire Myntra application.

The purpose is to demonstrate one specific product concept:

> Transform Wishlist from a passive collection of saved products into an active decision-making workspace that helps users resolve purchase uncertainty and move toward a quality purchase.

The central product problem is:

Users browse products and save multiple items to Wishlist, but saving an item does not necessarily mean they are ready to buy it.

Users may postpone the purchase because they are uncertain about:

- Whether the product is worth the price
- Which shortlisted product is better
- Whether the product quality is reliable
- Whether the fit/size will work
- What existing buyers actually liked or disliked
- Whether there is a better alternative
- Whether the current price is attractive
- Whether they should buy now or wait
- Which product best matches their personal priorities

The MVP introduces AI-powered decision support directly inside Wishlist.

> **IMPORTANT:** There must **NOT** be a separate "Decision Studio" page. The decision-support experience must be embedded within Wishlist.

---

## 2. Product Vision

The product vision is:

> Help users turn saved intent into resolved purchase decisions.

The experience should follow:

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

The system should **not** optimize simply for:

- more Wishlist additions
- longer sessions
- more product browsing
- more AI interactions

The product should optimize for:

> Better decisions from products the user has already shown interest in.

---

## 3. Business Goal

The broader business goal is:

Increase the percentage of users who purchase at least one item from their Wishlist within 30 days of adding it.

Conceptually:

```
Wishlist additions
    ↓
Resolved decisions
    ↓
Wishlist-to-Bag conversion
    ↓
Wishlist-to-Purchase conversion
```

The MVP does not need to implement production analytics, but the product experience should clearly demonstrate this funnel.

---

## 4. Product Goal

The product goal is:

> Reduce genuine purchase uncertainty without adding unnecessary friction or manufacturing confidence.

The system should help answer:

- "Which one should I buy?"
- "Is this worth the price?"
- "What are the common complaints?"
- "Is the quality reliable?"
- "Is the fit reliable?"
- "Is there a better option?"
- "Should I buy this now?"
- "Why should I choose this over another product?"

---

## 5. Target Experience

The user should feel:

> "I already saved these products because I am interested in them. Now Myntra is helping me decide."

The user should **NOT** feel:

> "I have entered a separate AI application."

The AI should feel like an intelligent layer embedded in the shopping experience.

Avoid:

- Creating a ChatGPT-like interface
- Creating an analytics-dashboard appearance
- Creating a research-tool appearance

The experience should still feel like a modern fashion-commerce application.

---

## 6. MVP Application Structure

The MVP should contain these primary sections:

1. Home
2. Product Listing / Category
3. Product Detail
4. Wishlist
5. Bag
6. Profile

The exact navigation can be simplified if necessary.

### DO NOT CREATE:

- Separate Decision Studio page
- Separate comparison page
- Separate AI assistant page
- Separate review-analysis page
- Separate price-analysis page
- Separate alerts page

All of these capabilities should happen **contextually inside Wishlist**.

---

## 7. Core UX Principle

### WISHLIST = DECISION WORKSPACE

Wishlist should not simply display:

- Product image
- Product name
- Price
- Heart icon

It should also expose useful decision signals.

Example:

```
MY WISHLIST

12 items saved

[Product Image]

Roadster
Floral Printed Dress

₹1,299
⭐ 4.4 (2,847)

Decision signals:
✓ Highly rated
✓ Good value
⚠ Some fit concerns

[Compare] [Insights] [Ask a Question]
```

The exact UI can change. The principle cannot:

> Users should be able to resolve uncertainty without leaving Wishlist.

---

## 8. Primary MVP Features

The Wishlist decision layer should contain these capabilities:

1. Product comparison
2. Price analysis
3. Review intelligence
4. Ask Me a Question
5. Similar-product detection
6. Decision-overload detection
7. Price-drop alerts
8. Evidence-based recommendation
9. Add selected product to Bag

---

## 9. Feature 1 — Product Comparison

Users should be able to select 2–3 Wishlist products and compare them.

Comparison should include:

- Product name
- Brand
- Price
- MRP
- Discount
- Rating
- Rating count
- Review themes
- Quality signals
- Fit signals
- Material
- Occasion
- Color
- Relevant product attributes
- User preference match

Example:

| | PRODUCT A | PRODUCT B | PRODUCT C |
|---|---|---|---|
| Price | ₹999 | ₹1,299 | ₹899 |
| Rating | 4.2 | 4.5 | 4.1 |
| Ratings | 1,200 | 2,800 | 650 |
| Quality | Good | Very Good | Good |
| Fit | Good | Good | Mixed |
| Value | High | Medium | Very High |

The system should **NOT** simply declare a winner without explanation. Instead, explain trade-offs.

Example:

```
BEST VALUE
Product C

BEST REVIEWED
Product B

BEST BALANCE
Product A

Why:
Product C is cheapest, but Product B has stronger review
evidence and fewer fit concerns. Product A provides the
best balance between price, rating, and quality signals.
```

The comparison should be understandable to a normal shopper.

---

## 10. Feature 2 — Price Analysis

Price analysis must happen inside Wishlist.

For every product where price data is available, display:

- Current price
- MRP
- Discount
- Saved price, if tracked
- Historical prices
- Lowest observed price
- Highest observed price
- Current price relative to historical range

Example:

```
PRICE INSIGHT

Current price:
₹1,199

Your saved price:
₹1,499

You save:
₹300

30-day lowest:
₹1,099

Decision:
Good price, but not the lowest observed price.
```

The system should **NOT** claim future price movements with certainty.

Do **NOT** say:

> "The price will drop tomorrow."

Instead say:

> "The current price is close to the recent low."

or:

> "This item has previously dropped below the current price."

---

## 11. Price History Data

For the MVP, price history can be seeded.

Example:

```json
{
  "product_id": "P001",
  "price_history": [
    { "date": "2026-08-01", "price": 1499 },
    { "date": "2026-08-10", "price": 1299 },
    { "date": "2026-08-20", "price": 1499 },
    { "date": "2026-08-30", "price": 1199 }
  ]
}
```

The price-analysis engine should calculate:

- Current price
- Historical minimum
- Historical maximum
- Difference from saved price
- Difference from historical minimum
- Relative price position

---

## 12. Feature 3 — Review Intelligence

Review intelligence is one of the most important parts of this project.

The system should **NOT** only calculate:

> "Positive sentiment = 82%"

That is insufficient. The system should identify recurring themes.

Potential review themes:

- Fit
- Size accuracy
- Fabric
- Material
- Comfort
- Quality
- Durability
- Color accuracy
- Appearance
- Value for money
- Stitching
- Transparency/thickness
- Occasion suitability
- Product-image accuracy
- Common complaints

Example:

```
WHAT BUYERS LIKE

✓ Looks similar to product images
✓ Comfortable
✓ Good design
✓ Good value for money

COMMON CONCERNS

⚠ Fabric feels thin
⚠ Some users report loose fitting

REVIEW SIGNAL

Mostly positive, with fabric thickness as the
main recurring concern.
```

> **IMPORTANT:** AI must **NOT** invent review evidence.

If there are only 3 reviews, do not write:

> "Most buyers..."

Instead write:

> "Among the available reviews..."

---

## 13. Review Data Model

Example raw review:

```json
{
  "review_id": "R001",
  "product_id": "P001",
  "rating": 4,
  "review_text": "The dress looks exactly like the picture. Fabric is comfortable but slightly thin.",
  "review_date": "2026-07-15"
}
```

A processed review insight object can look like:

```json
{
  "product_id": "P001",
  "themes": {
    "fit": { "positive": 12, "negative": 4 },
    "fabric": { "positive": 8, "negative": 15 },
    "comfort": { "positive": 21, "negative": 2 }
  }
}
```

These numbers should come from actual available review data. **Never fabricate them.**

---

## 14. Feature 4 — Ask Me a Question

Wishlist should contain an "Ask Me a Question" interaction.

For the MVP, this should **NOT** be an unrestricted chatbot. Use predefined questions/scenarios.

Example:

```
ASK ME A QUESTION

What would you like to know?

○ Is this worth the price?
○ What do buyers dislike about it?
○ Is the fit reliable?
○ How is the fabric quality?
○ Is there a better option in my Wishlist?
○ Which one should I buy?
○ Why is this better than Product B?
○ Should I wait for a better price?
```

The user selects a question. The backend retrieves relevant structured data. The AI synthesizes the answer.

---

## 15. Question → Reasoning Model

Each question should have a defined reasoning flow.

**Example — QUESTION:** "Is this worth the price?"

**INPUTS:**

- Current price
- MRP
- Price history
- Rating
- Rating count
- Review themes
- Similar Wishlist products
- User preferences

**PROCESS:**

1. Calculate price position.
2. Identify quality/review evidence.
3. Compare with similar Wishlist items.
4. Check whether product matches user priorities.
5. Generate evidence-based explanation.
6. State uncertainty if evidence is weak.

**OUTPUT:**

```
Worth the price?
🟡 Mostly

Why:

✓ Strong rating from 2,800+ ratings
✓ Positive feedback around comfort
✓ Better reviewed than two similar Wishlist products

Main concern:

⚠ Some reviews mention thin fabric.

Verdict:

Worth ₹1,299 if comfort and design are priorities.
A cheaper Wishlist alternative offers better price value.
```

---

## 16. Facts vs. Interpretation

The AI response should separate:

- **FACT** — "Current price is ₹1,299."
- **EVIDENCE** — "2,800+ ratings and recurring positive feedback about comfort."
- **INTERPRETATION** — "This suggests relatively strong value for shoppers prioritizing comfort."
- **RECOMMENDATION** — "Choose this if comfort matters more than minimizing price."

Do not present interpretation as fact.

---

## 17. Feature 5 — Similar Product Detection

The system should identify products that are similar to Wishlist products.

For the MVP, similarity should primarily use structured attributes:

- Category
- Subcategory
- Style
- Color
- Material
- Fit
- Occasion
- Price range
- Brand
- Product attributes

Example:

```
Wishlist product:
Nike Sneakers
₹4,999
⭐ 4.2

Similar product:
Adidas Sneakers
₹3,999
⭐ 4.5
```

The system can surface:

```
SIMILAR PRODUCT FOUND

Adidas Sneakers
₹3,999
⭐ 4.5

₹1,000 cheaper
Higher rating

[Compare]
```

The recommendation must be explainable.

---

## 18. Feature 6 — Decision Overload

Users may save too many similar products.

Example: 5 similar dresses in Wishlist.

The system should detect this and surface:

```
"You have 5 similar dresses saved.
Want help narrowing them down?"

[Compare My Options]
```

This should be a contextual card/modal/bottom sheet. **Do not create a separate decision page.**

---

## 19. Feature 7 — Price Alert

Price alerts should appear as contextual overlays.

Example:

```
🔔 PRICE DROP

Your Wishlist item dropped

₹1,499 → ₹1,199

You save ₹300.

[View Item]
[Dismiss]
```

The alert should be triggered by mock/seeded price data in the MVP. The system should not require real-time pricing infrastructure.

---

## 20. Feature 8 — Similar Product Alert

Example:

```
✨ SIMILAR PRODUCT FOUND

You may also want to consider:

Adidas Sneakers
₹3,999
⭐ 4.5

₹1,000 cheaper
Higher rating

[Compare]
[Dismiss]
```

This should appear as a Modal, Bottom sheet, Toast, or Inline card, depending on the UI design.

---

## 21. Feature 9 — Decision Recommendation

The system should be able to recommend a product when the user asks: "Which one should I buy?"

The recommendation should be based on:

- User priorities
- Price
- Rating
- Rating count
- Review themes
- Fit
- Material
- Occasion
- Product similarity
- Available evidence

Example:

```
BEST MATCH FOR YOU

Product A

Why:

✓ Within your budget
✓ Strong comfort reviews
✓ Suitable for casual wear
✓ Better balance of price and rating

Trade-off:

Product B has stronger overall ratings,
but costs ₹300 more.
```

The recommendation must remain conditional.

Avoid: "This is definitely the best."

Prefer: "Best match based on your stated preference for price and comfort."

---

## 22. User Profile / Preferences

The MVP can have lightweight user preference information.

Example:

```json
{
  "user_id": "U001",
  "size": "M",
  "price_min": 500,
  "price_max": 1500,
  "occasions": ["Casual", "Office"],
  "priority": ["Quality", "Comfort"]
}
```

This should influence decision support.

- If the user prioritizes price → the system should give more weight to price/value.
- If the user prioritizes quality → the system should give more weight to review/quality evidence.

---

## 23. Product Data Model

```json
{
  "product_id": "P001",
  "brand": "Roadster",
  "name": "Women Floral Printed Dress",
  "gender": "Women",
  "category": "Dresses",
  "subcategory": "Casual Dresses",

  "price": 899,
  "mrp": 1999,
  "discount": 55,

  "rating": 4.3,
  "rating_count": 2847,

  "image_url": "...",
  "product_url": "...",

  "sizes": ["S", "M", "L", "XL"],
  "colors": ["Blue"],

  "fit": "Regular",
  "material": "Viscose",

  "occasions": ["Casual", "Vacation"]
}
```

Additional fields can be added when useful.

---

## 24. Wishlist Data Model

Single item example:

```json
{
  "user_id": "U001",
  "product_id": "P001",
  "added_at": "2026-08-15",
  "saved_price": 1499
}
```

A user can have multiple Wishlist items:

```json
{
  "user_id": "U001",
  "product_ids": ["P001", "P014", "P022"]
}
```

---

## 25. Bag Data Model

```json
{
  "user_id": "U001",
  "product_ids": ["P014"]
}
```

The MVP does not need real payment processing. The funnel can end at:

```
Wishlist
    ↓
Decision
    ↓
Add to Bag
    ↓
Mock Checkout
    ↓
Purchase Confirmation
```

---

## 26. Data Strategy

Do **NOT** attempt to reproduce the entire Myntra catalog.

**Recommended starting dataset:** 50–100 products, approximately:

- 5–10 categories
- 10–15 products with meaningful review data
- 20–50 reviews for selected products
- Price history for selected products
- Several intentionally similar/overlapping products

The dataset should be designed to create meaningful decision scenarios. For example:

| Product | Price | Rating | Ratings |
|---|---|---|---|
| A | ₹999 | 4.2 | 1,200 |
| B | ₹1,299 | 4.5 | 2,800 |
| C | ₹899 | 4.1 | 650 |

This allows the system to demonstrate:

- Lowest price → C
- Best reviewed → B
- Best balance → A

---

## 27. Real Data / Scraping Strategy

The MVP may eventually use real product data. However:

> **DO NOT** make the application dependent on a live Myntra scraper.

The architecture must separate **DATA SOURCE** from **APPLICATION LOGIC**.

Recommended architecture:

```
                    DATA SOURCES
                         |
             +-----------+-----------+
             |                       |
        Seed Dataset          External Data
             |                       |
             +-----------+-----------+
                         |
                    DATA MODEL
                         |
                      DATABASE
                         |
                    BACKEND API
                         |
                 AI / DECISION LAYER
                         |
                      FRONTEND
```

This means the application can initially use `products.json`, `reviews.json`, `price-history.json` and later replace/augment those with external data.

When using real external data, respect applicable website terms, access restrictions, copyright, privacy requirements, and rate limits.

**Do not design the scraper around bypassing anti-bot protections.**

---

## 28. Data Ingestion Layer

Create a replaceable data-ingestion abstraction.

```
DataSource
    ↓
normalizeProduct()
    ↓
normalizeReview()
    ↓
normalizePriceHistory()
    ↓
Database
```

The frontend should never depend directly on scraped HTML.

```
External data
    ↓
Parser
    ↓
Normalized product object
    ↓
Database
```

This makes the application maintainable.

---

## 29. Database Structure

At minimum, support these logical entities:

**PRODUCTS**
- product_id, brand, name, category, subcategory, price, mrp, discount, rating, rating_count, image_url, product_url, sizes, colors, fit, material, occasions

**REVIEWS**
- review_id, product_id, rating, review_text, review_date

**PRICE_HISTORY**
- price_history_id, product_id, date, price

**USERS**
- user_id, preferences

**WISHLIST**
- user_id, product_id, added_at, saved_price

**BAG**
- user_id, product_id

**REVIEW_INSIGHTS**
- product_id, theme, positive_count, negative_count, summary

---

## 30. AI Architecture

Use AI only where reasoning/synthesis provides meaningful value. Do **NOT** use AI for simple calculations.

### Deterministic application logic

Use normal code for:

- Price calculations
- Discount calculations
- Filtering
- Sorting
- Rating aggregation
- Price history calculations
- Wishlist CRUD
- Bag CRUD
- Basic similarity
- Data validation

### AI

Use AI for:

- Review theme extraction
- Review summarization
- Evidence synthesis
- Natural-language explanation
- Trade-off explanation
- Predefined question answering
- Recommendation explanations

**Architecture:**

```
PRODUCT DATA
+
REVIEW DATA
+
PRICE DATA
+
USER PREFERENCES
        ↓
STRUCTURED EVIDENCE
        ↓
AI DECISION LAYER
        ↓
USER-FACING EXPLANATION
```

---

## 31. Review Analysis Pipeline

```
Raw reviews
    ↓
Clean / normalize
    ↓
Extract themes
    ↓
Classify sentiment by theme
    ↓
Aggregate evidence
    ↓
Generate structured review insights
    ↓
Use inside Wishlist (no separate Decision Studio page)
```

Potential themes: FIT, FABRIC, QUALITY, COMFORT, COLOR, DURABILITY, VALUE, APPEARANCE, SIZE, OCCASION.

---

## 32. AI Grounding Rule

The AI must only make claims supported by available data.

If information is missing, say:

> "Not enough review data to assess fit confidently."

Do **NOT** say:

> "Fit is excellent." — unless evidence supports it.

Similarly, if there are no price-history records, do **NOT** say:

> "This is the lowest price."

Instead say:

> "Price history unavailable."

---

## 33. Decision Confidence

Confidence should reflect evidence strength. It should **NOT** be presented as "AI confidence = 95%".

Instead, confidence can be:

- **HIGH** — Large review volume, consistent review themes, clear product attributes, strong comparison data
- **MEDIUM** — Moderate review volume, some conflicting evidence
- **LOW** — Very few reviews, missing attributes, conflicting evidence

Example:

```
Decision confidence:
HIGH

Reason:
Strong rating volume and consistent review evidence.
```

---

## 34. Recommendation Logic

Start with explainable deterministic scoring.

```
Product relevance =
    price fit
  + occasion fit
  + quality match
  + rating signal
  + review signal
  + user preference match
```

Then use AI to explain the score.

Do **NOT** build a complex ML recommendation engine for the first MVP. The purpose is to demonstrate **DECISION SUPPORT**, not production-scale personalization infrastructure.

---

## 35. Product Similarity Logic

Initial similarity can use structured attributes:

- Category match
- Subcategory match
- Style match
- Occasion match
- Material match
- Fit match
- Color match
- Price proximity
- Brand similarity

```
similarity_score =
    category_match
    + style_match
    + occasion_match
    + material_match
    + price_proximity
```

Embeddings/vector search can be introduced later if required. Do not over-engineer the first version.

---

## 36. Frontend Components

Suggested reusable components:

- `ProductCard`
- `WishlistCard`
- `WishlistHeader`
- `CompareSelector`
- `CompareDrawer`
- `ComparisonTable`
- `InsightCard`
- `PriceInsight`
- `ReviewInsight`
- `QuestionSheet`
- `QuestionOption`
- `RecommendationCard`
- `SimilarProductAlert`
- `PriceAlert`
- `DecisionOverloadModal`
- `AddToBagButton`
- `Toast`
- `BottomSheet`

Components should be reusable. Avoid duplicating similar UI logic.

---

## 37. Suggested Project Structure

```
myntra-decision-studio/

frontend/
    Home/
    ProductListing/
    ProductDetail/
    Wishlist/
    Bag/
    Profile/

components/
    ProductCard/
    WishlistCard/
    CompareDrawer/
    ComparisonTable/
    InsightPanel/
    PriceInsight/
    ReviewInsight/
    QuestionSheet/
    AlertModal/
    RecommendationCard/

backend/
    products/
    reviews/
    wishlist/
    comparison/
    price-analysis/
    recommendations/
    questions/

ai/
    review-analyzer/
    product-comparator/
    question-answering/
    recommendation-engine/
    prompts/

data/
    products.json
    reviews.json
    price-history.json

context.md
```

The exact framework can follow the existing project setup. Do not introduce unnecessary technologies.

---

## 38. User Flow — Browse to Wishlist

```
Home
    ↓
Category
    ↓
Product Listing
    ↓
Product Detail
    ↓
Add to Wishlist
    ↓
Wishlist
```

The user should be able to see a meaningful confirmation when a product is added.

---

## 39. User Flow — Wishlist to Comparison

```
Wishlist
    ↓
Select 2–3 products
    ↓
Compare
    ↓
Price / Rating / Reviews / Fit / Quality / Value
    ↓
Trade-off explanation
    ↓
Choose product
    ↓
Add to Bag
```

---

## 40. User Flow — Ask a Question

```
Wishlist
    ↓
Product
    ↓
Ask Me a Question
    ↓
Select predefined question
    ↓
Retrieve relevant evidence
    ↓
AI synthesis
    ↓
Answer
    ↓
Optional recommendation
    ↓
Add to Bag
```

---

## 41. User Flow — Price Alert

```
Wishlist
    ↓
Price changes in mock dataset
    ↓
Alert triggered
    ↓
Popup / Bottom Sheet
    ↓
View Product
    ↓
Decision
    ↓
Add to Bag
```

---

## 42. User Flow — Similar Product

```
Wishlist
    ↓
Similarity detection
    ↓
Similar product found
    ↓
Contextual alert
    ↓
Compare
    ↓
Choose
    ↓
Add to Bag
```

---

## 43. User Flow — Decision Overload

```
Wishlist
    ↓
Detect many similar products
    ↓
Show: "You have 5 similar dresses saved."
    ↓
"Want help narrowing them down?"
    ↓
Compare My Options
    ↓
Comparison
    ↓
Recommendation
    ↓
Decision
```

---

## 44. MVP Decision Scenarios

The demo should support these scenarios especially well:

1. "Which one should I buy?"
2. "Is this worth the price?"
3. "What do buyers dislike about it?"
4. "Is the fit reliable?"
5. "How is the fabric quality?"
6. "Is there a better option in my Wishlist?"
7. "Should I wait for a better price?"
8. "I have saved too many similar products."

These scenarios demonstrate the product value.

---

## 45. UI Design Principles

The UI should feel like a modern fashion-commerce app.

Prioritize:

- Product imagery
- Clean product cards
- Clear price hierarchy
- Rating visibility
- Easy Wishlist actions
- Minimal cognitive load
- Contextual AI
- Mobile-friendly interaction
- Familiar shopping patterns
- Clear calls to action

AI should be visually secondary to the shopping experience. Do not make every component look like AI.

---

## 46. AI UI Principles

Avoid: "AI says..."

Instead use:

- "Decision insight"
- "Why this may be a better fit"
- "Based on buyer reviews"
- "Price insight"
- "Common concerns"
- "Similar option"

The system should feel intelligent without constantly announcing AI.

---

## 47. Error / Missing Data Handling

If data is missing, show an appropriate fallback:

| Missing data | Fallback message |
|---|---|
| No review data | "Not enough review data to assess this reliably." |
| No price history | "Price history unavailable." |
| No size data | "Size availability information unavailable." |
| No similar products | "No closely matching products found." |

**Never fabricate information to fill gaps.**

---

## 48. What NOT to Build

Do **NOT** build in the first MVP:

- Entire Myntra catalog
- Production payment system
- Real payment gateway
- Full authentication infrastructure
- Real-time inventory infrastructure
- Seller dashboard
- Order management system
- Advanced ML recommendation system
- Large-scale vector database unless necessary
- Production-grade scraping infrastructure
- Unrestricted AI chatbot
- Separate Decision Studio page
- Separate comparison page
- Separate AI assistant page
- Complex notification infrastructure

The goal is: **SMALLEST CONVINCING END-TO-END EXPERIENCE**

---

## 49. MVP Data Target

Use approximately:

- **50–100 products**
- **5–10 categories**
- **10–15 products** with detailed reviews
- **20–50 reviews** for selected products
- Price history for selected products
- Several groups of similar products

Example groups:

- **Group 1 — Dresses**: 3–5 similar dresses
- **Group 2 — Sneakers**: 3–5 similar sneakers
- **Group 3 — Handbags**: 3–5 similar handbags
- **Group 4 — Tops**: 3–5 similar tops
- **Group 5 — Jeans**: 3–5 similar jeans

This allows comparison and recommendation scenarios.

---

## 50. Data Quality Requirements

The seed dataset should be internally consistent **for attributes that reviews discuss**.

`products.rating` and `products.rating_count` are catalog fields (they may look like a live storefront). Review intelligence must use **actual review rows** in the database. Do not write “2,800 buyers mentioned thin fabric” unless 2,800 review texts exist. Prefer “Among the available reviews…”.

If the product says `fit = Regular`, reviews should not overwhelmingly claim "Very tight fit" unless the demo is intentionally showing conflicting evidence.

The dataset should contain both positive and negative review signals. This is important because Decision Studio needs trade-offs.

---

## 51. IMPORTANT — Do Not Hallucinate Data

**This is a hard rule.**

The system must never invent:

- Product specifications
- Reviews
- Ratings
- Rating counts
- Prices
- Discounts
- Price history
- Fit claims
- Material claims
- Buyer opinions

If the dataset does not contain information, explicitly state that information is unavailable.

---

## 52. Recommendation Transparency

Every recommendation should answer: **WHY?**

Example:

```
RECOMMENDED FOR YOU

Product A

Why:

✓ ₹999 — within your budget
✓ 4.4 rating from 2,000+ ratings
✓ Strong comfort signals
✓ Matches your casual-use preference

Trade-off:

Product B has better ratings but costs ₹300 more.
```

This makes the recommendation explainable.

---

## 53. Decision Studio Is Not a Chatbot

The core product is **not**: "Ask AI anything about shopping."

The core product is: "Help me resolve a decision about products I already saved."

Therefore, the primary UI should be:

```
Wishlist
    ↓
Decision signals
    ↓
Comparison
    ↓
Question
    ↓
Evidence
    ↓
Decision
```

The AI is an enabling layer. It is not the product itself.

---

## 54. Success Criteria for Demo

The MVP should allow a user to:

1. Open the app
2. Browse products
3. Open product details
4. Add products to Wishlist
5. Open Wishlist
6. See decision-support signals
7. Select multiple products
8. Compare them
9. See price analysis
10. See review insights
11. Ask a predefined question
12. Receive an evidence-based answer
13. Receive a similar-product suggestion
14. Receive a price-drop alert
15. See a decision-overload prompt
16. Select a product
17. Add it to Bag
18. Complete a mock checkout/purchase flow

---

## 55. Primary Demo Story

The strongest demo flow should be:

```
USER BROWSES
    ↓
USER SAVES 3 SIMILAR PRODUCTS
    ↓
WISHLIST
    ↓
SYSTEM IDENTIFIES DECISION OVERLOAD
    ↓
"YOU HAVE 3 SIMILAR PRODUCTS SAVED"
    ↓
COMPARE
    ↓
USER SEES:
- Price
- Rating
- Review evidence
- Fit
- Quality
- Value
    ↓
USER ASKS:
"WHICH ONE SHOULD I BUY?"
    ↓
SYSTEM EXPLAINS TRADE-OFFS
    ↓
RECOMMENDATION
    ↓
USER CHECKS PRICE INSIGHT
    ↓
PRICE ALERT / CURRENT PRICE
    ↓
USER MAKES DECISION
    ↓
ADD TO BAG
```

This is the primary end-to-end product story.

---

## 56. Product Principle

The application should follow this principle throughout development:

> **DON'T HELP USERS SAVE MORE PRODUCTS.**
>
> **HELP THEM CONFIDENTLY RESOLVE WHICH SAVED PRODUCT IS RIGHT FOR THEM.**

The system should reduce genuine uncertainty around:

- Price
- Quality
- Fit
- Reviews
- Alternatives
- Personal relevance

and help turn resolved decisions into quality purchases.

---

## 57. Cursor Implementation Rules

When implementing this project in Cursor:

1. Read this context before making architectural changes.
2. Preserve the Wishlist-centered decision experience.
3. Do not create a separate Decision Studio page.
4. Reuse existing components where possible.
5. Keep frontend, backend, data, and AI logic separated.
6. Use deterministic code for calculations.
7. Use AI for synthesis and explanation.
8. Keep seeded data realistic.
9. Never fabricate data.
10. Keep data ingestion replaceable.
11. Do not hard-code AI responses when the answer can be generated from data.
12. Make recommendations explainable.
13. Handle missing data explicitly.
14. Keep the UI mobile-friendly.
15. Avoid unnecessary dependencies.
16. Do not rewrite unrelated working features.
17. Build one end-to-end feature at a time.
18. Test each feature before moving to the next.
19. Prefer simple architecture over premature production-scale infrastructure.
20. Maintain the ability to replace mock data with real/collected data later.

---

## 58. Implementation Priority

Build in this order. **Phase 0** (repo scaffold) is required because this project starts greenfield; it is specified in `Docs/Phase_wise_Implementation.md` and `Docs/Doc_Alignment.md`.

**PHASE 0 — Foundation (implementation plan)**
- React + Vite, FastAPI, SQLite path, `.env.example`
- No Groq calls, no decision features

**PHASE 1 — Basic Myntra-like shell**
- Home
- Product listing
- Product detail
- Wishlist
- Bag
- Profile

**PHASE 2 — Product data**
- Products
- Reviews
- Price history
- Users
- Wishlist

**PHASE 3 — Wishlist decision UI**
- Decision signals
- Compare
- Price insight
- Review insight

**PHASE 4 — Ask Me a Question**
- Predefined questions
- Backend retrieval
- AI response
- Evidence grounding

**PHASE 5 — Smart alerts**
- Price drop
- Similar product
- Decision overload

**PHASE 6 — Polish**
- Loading states
- Empty states
- Error states
- Responsive UI
- Animations
- Visual consistency

Do **NOT** start with advanced AI. First make the basic shopping experience work.

---

## 59. Architecture Principle

Keep the architecture simple:

```
FRONTEND
    ↓
BACKEND API
    ↓
DATA / DATABASE
    ↓
AI SERVICES
```

- The frontend should never directly call external scraping sources.
- The AI layer should never directly manipulate UI state.
- The database should remain the source of truth for product/review/price data.

---

## 60. Final Product Definition

This project is a:

**Myntra-like fashion shopping MVP**

with:

**AI-powered Wishlist decision support**

where:

```
Wishlist
    ↓
becomes
    ↓
Decision Workspace
```

The product helps users:

**SAVE → COMPARE → UNDERSTAND → QUESTION → EVALUATE → DECIDE → BUY**

without requiring a separate Decision Studio application.

The MVP succeeds when the user can move from:

> "I like these products but I don't know which one to buy"

to:

> "I understand the trade-offs and know which one is right for me."

**That is the core purpose of this project.**

---

## 61. Alignment with implementation docs

Canonical locks (API paths, `saved_price` first-save-wins, ₹1 price-drop, question registry, fallback copy): **`Docs/Doc_Alignment.md`**.

Implement using `Docs/Phase_wise_Implementation.md` starting at Phase 0. Stack: React + Vite, FastAPI, SQLite, Groq (free). No separate Decision Studio page.
