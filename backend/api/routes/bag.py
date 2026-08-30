from fastapi import APIRouter, Depends, HTTPException

from backend.api.deps import get_user_id
from backend.db.repositories import bag as bag_repo
from backend.db.session import get_connection
from backend.models import ProductIdBody

router = APIRouter(prefix="/api/bag", tags=["bag"])


@router.get("")
def get_bag(user_id: str = Depends(get_user_id)):
    conn = get_connection()
    try:
        items = bag_repo.list_bag(conn, user_id)
        total = sum(i.product.price * i.quantity for i in items)
        return {"items": items, "count": len(items), "total": total}
    finally:
        conn.close()


@router.post("")
def add_to_bag(body: ProductIdBody, user_id: str = Depends(get_user_id)):
    conn = get_connection()
    try:
        item = bag_repo.add_to_bag(conn, user_id, body.product_id)
        if not item:
            raise HTTPException(status_code=404, detail="Product not found")
        return item
    finally:
        conn.close()


@router.delete("/{product_id}", status_code=204)
def remove_from_bag(product_id: str, user_id: str = Depends(get_user_id)):
    conn = get_connection()
    try:
        removed = bag_repo.remove_from_bag(conn, user_id, product_id)
        if not removed:
            raise HTTPException(status_code=404, detail="Bag item not found")
    finally:
        conn.close()
