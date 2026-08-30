const WOMEN_APPAREL = {
  XS: 'Bust 30-32" · Waist 24-26"',
  S: 'Bust 32-34" · Waist 26-28"',
  M: 'Bust 34-36" · Waist 28-30"',
  L: 'Bust 36-38" · Waist 30-32"',
  XL: 'Bust 38-40" · Waist 32-34"',
  XXL: 'Bust 40-42" · Waist 34-36"',
};

const MEN_APPAREL = {
  XS: 'Chest 34-36" · Waist 28-30"',
  S: 'Chest 36-38" · Waist 30-32"',
  M: 'Chest 38-40" · Waist 32-34"',
  L: 'Chest 40-42" · Waist 34-36"',
  XL: 'Chest 42-44" · Waist 36-38"',
  XXL: 'Chest 44-46" · Waist 38-40"',
};

const FOOTWEAR = {
  "6": "UK 6 · 24.5 cm",
  "7": "UK 7 · 25.5 cm",
  "8": "UK 8 · 26.5 cm",
  "9": "UK 9 · 27.5 cm",
  "10": "UK 10 · 28.5 cm",
  "11": "UK 11 · 29.5 cm",
};

function chartForProduct(product) {
  const cat = (product.category || "").toLowerCase();
  const gender = (product.gender || "").toLowerCase();
  if (cat.includes("sneaker") || cat.includes("sandal") || cat === "footwear") {
    return FOOTWEAR;
  }
  if (gender.includes("men")) return MEN_APPAREL;
  return WOMEN_APPAREL;
}

export function getSizeInfo(product, size) {
  if (!size) return "";
  const chart = chartForProduct(product);
  const detail = chart[size];
  const fit = product.fit ? `${product.fit} fit` : "Standard fit";
  if (detail) return `${size} — ${detail} · ${fit}`;
  return `${size} — ${fit}`;
}

export function sizeGuideLabel(product) {
  const cat = (product.category || "").toLowerCase();
  if (cat.includes("sneaker") || cat.includes("sandal")) return "Select UK size";
  return "Select size";
}
