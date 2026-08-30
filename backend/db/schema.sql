-- Phase 2+ schema. Catalog loaded via offline ingest_catalog job.

CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    display_name TEXT,
    size TEXT,
    price_min INTEGER,
    price_max INTEGER,
    occasions TEXT,
    priorities TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    brand TEXT NOT NULL,
    name TEXT NOT NULL,
    gender TEXT,
    category TEXT,
    subcategory TEXT,
    style TEXT,
    price INTEGER NOT NULL,
    mrp INTEGER NOT NULL,
    discount INTEGER,
    rating REAL,
    rating_count INTEGER,
    image_url TEXT,
    product_url TEXT,
    sizes TEXT,
    colors TEXT,
    fit TEXT,
    material TEXT,
    occasions TEXT,
    attributes_json TEXT,
    updated_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);

CREATE TABLE IF NOT EXISTS reviews (
    review_id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    rating REAL,
    review_text TEXT,
    review_date TEXT,
    source_batch_id TEXT,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE INDEX IF NOT EXISTS idx_reviews_product ON reviews(product_id);

CREATE TABLE IF NOT EXISTS review_insights (
    product_id TEXT NOT NULL,
    theme TEXT NOT NULL,
    positive_count INTEGER,
    negative_count INTEGER,
    summary TEXT,
    evidence_review_ids TEXT,
    confidence TEXT,
    updated_at TEXT,
    PRIMARY KEY (product_id, theme),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL,
    date TEXT NOT NULL,
    price INTEGER NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE INDEX IF NOT EXISTS idx_price_history_product ON price_history(product_id, date);
CREATE UNIQUE INDEX IF NOT EXISTS idx_price_history_unique ON price_history(product_id, date);

CREATE TABLE IF NOT EXISTS price_stats (
    product_id TEXT PRIMARY KEY,
    current_price INTEGER,
    min_price INTEGER,
    max_price INTEGER,
    avg_price REAL,
    min_date TEXT,
    relative_position TEXT,
    updated_at TEXT,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS product_similarity (
    product_id TEXT NOT NULL,
    similar_product_id TEXT NOT NULL,
    score REAL,
    matched_attributes TEXT,
    reason TEXT,
    PRIMARY KEY (product_id, similar_product_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (similar_product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS wishlist_items (
    user_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    added_at TEXT NOT NULL,
    saved_price INTEGER NOT NULL,
    occasion TEXT DEFAULT 'General',
    size TEXT,
    PRIMARY KEY (user_id, product_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS bag_items (
    user_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    added_at TEXT NOT NULL,
    PRIMARY KEY (user_id, product_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    product_ids TEXT,
    created_at TEXT,
    status TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    type TEXT NOT NULL,
    product_id TEXT,
    payload_json TEXT,
    created_at TEXT,
    dismissed_at TEXT,
    seen_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE INDEX IF NOT EXISTS idx_alerts_user ON alerts(user_id);
