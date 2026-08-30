from fastapi import APIRouter, Depends, HTTPException, Query

from backend.api.deps import get_user_id
from backend.db.init_db import ensure_catalog_ready
from backend.db.repositories import products as product_repo
from backend.db.session import get_connection
from backend.models import CategoryOut
from backend.services import insight_service

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("")
def list_products(category: str | None = Query(None)):
    ensure_catalog_ready()
    conn = get_connection()
    try:
        items = product_repo.list_products(conn, category=category)
        return {"products": items}
    finally:
        conn.close()


@router.get("/categories/list", response_model=list[CategoryOut])
def list_categories():
    ensure_catalog_ready()
    conn = get_connection()
    try:
        return [CategoryOut(name=n, count=c) for n, c in product_repo.list_categories(conn)]
    finally:
        conn.close()


@router.get("/{product_id}/price-insight")
def get_price_insight(product_id: str, user_id: str = Depends(get_user_id)):
    conn = get_connection()
    try:
        payload = insight_service.get_price_insight_for_product(conn, user_id, product_id)
        if not payload:
            raise HTTPException(status_code=404, detail="Product not found")
        return payload
    finally:
        conn.close()


@router.get("/{product_id}/review-insight")
def get_review_insight(product_id: str):
    conn = get_connection()
    try:
        payload = insight_service.get_review_insight_for_product(conn, product_id)
        if not payload:
            raise HTTPException(status_code=404, detail="Product not found")
        return payload
    finally:
        conn.close()


@router.get("/{product_id}")
def get_product(product_id: str):
    conn = get_connection()
    try:
        product = product_repo.get_product(conn, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    finally:
        conn.close()
