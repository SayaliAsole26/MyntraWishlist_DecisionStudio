from typing import Any

from pydantic import BaseModel, Field


class ProductOut(BaseModel):
    product_id: str
    brand: str
    name: str
    gender: str | None = None
    category: str | None = None
    subcategory: str | None = None
    style: str | None = None
    price: int
    mrp: int
    discount: int | None = None
    rating: float | None = None
    rating_count: int | None = None
    image_url: str | None = None
    product_url: str | None = None
    sizes: list[str] = Field(default_factory=list)
    colors: list[str] = Field(default_factory=list)
    fit: str | None = None
    material: str | None = None
    occasions: list[str] = Field(default_factory=list)


class CategoryOut(BaseModel):
    name: str
    count: int


class ProductIdBody(BaseModel):
    product_id: str


class WishlistAddBody(BaseModel):
    product_id: str
    occasion: str | None = "General"
    size: str | None = None


class WishlistItemOut(BaseModel):
    product_id: str
    added_at: str
    saved_price: int
    occasion: str | None = "General"
    size: str | None = None
    product: ProductOut


class WishlistItemWithSignals(WishlistItemOut):
    signals: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)


class CompareBody(BaseModel):
    product_ids: list[str] = Field(min_length=2, max_length=3)
    need: str | None = None
    tradeoff_priority: str | None = None
    user_confidence: int | None = Field(default=None, ge=0, le=4)


class ShortlistBody(BaseModel):
    product_ids: list[str] = Field(min_length=1)
    need: str | None = None
    tradeoff_priority: str | None = None


class QuestionAnswerBody(BaseModel):
    question_id: str
    product_id: str | None = None
    product_ids: list[str] | None = None


class BagItemOut(BaseModel):
    product_id: str
    quantity: int
    added_at: str
    product: ProductOut


class ProfileOut(BaseModel):
    user_id: str
    display_name: str | None = None
    size: str | None = None
    price_min: int | None = None
    price_max: int | None = None
    occasions: list[str] = Field(default_factory=list)
    priorities: list[str] = Field(default_factory=list)


class ProfileUpdate(BaseModel):
    display_name: str | None = None
    size: str | None = None
    price_min: int | None = None
    price_max: int | None = None
    occasions: list[str] | None = None
    priorities: list[str] | None = None


class AlertOut(BaseModel):
    alert_id: str
    type: str
    product_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    product: ProductOut | None = None
    similar_product: ProductOut | None = None


class OverloadOut(BaseModel):
    alert_id: str | None = None
    group_key: str
    count: int
    label: str
    category: str | None = None
    subcategory: str | None = None
    product_ids: list[str] = Field(default_factory=list)


class CheckoutOut(BaseModel):
    order_id: str
    user_id: str
    product_ids: list[str]
    total: int
    item_count: int
    created_at: str
    status: str
