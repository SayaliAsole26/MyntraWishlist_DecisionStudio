"""Load catalog seed files from data/*.json."""

import json
from dataclasses import dataclass
from pathlib import Path

from backend.config import ROOT_DIR

DATA_DIR = ROOT_DIR / "data"


@dataclass
class SeedBundle:
    products: list[dict]
    reviews: list[dict]
    price_history: list[dict]
    users: list[dict]


class SeedFileSource:
    """Reads designed seed JSON. No network, no scrape."""

    def __init__(self, data_dir: Path | None = None):
        self.data_dir = data_dir or DATA_DIR

    def load(self) -> SeedBundle:
        products = self._read_json("products.json")
        reviews = self._read_json("reviews.json", default=[])
        price_history = self._read_json("price-history.json", default=[])
        users = self._read_json("users.json", default=[])
        return SeedBundle(
            products=products,
            reviews=reviews,
            price_history=price_history,
            users=users,
        )

    def _read_json(self, filename: str, default: list | None = None) -> list:
        path = self.data_dir / filename
        if not path.exists():
            if default is not None:
                return default
            raise FileNotFoundError(f"Seed file missing: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError(f"{filename} must be a JSON array")
        return data
