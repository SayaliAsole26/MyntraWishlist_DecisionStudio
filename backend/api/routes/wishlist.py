from fastapi import APIRouter, Depends, HTTPException, Path

from backend.api.deps import get_user_id
from backend.db.repositories import wishlist as wishlist_repo
from backend.db.session import get_connection
from backend.models import CompareBody, ShortlistBody, WishlistAddBody
from backend.services import compare_service, shortlist_service, wishlist_service

router = APIRouter(prefix="/api/wishlist", tags=["wishlist"])


@router.get("")
def get_wishlist(user_id: str = Depends(get_user_id)):
    conn = get_connection()
    try:
        return wishlist_service.get_wishlist_with_signals(conn, user_id)
    finally:
        conn.close()


@router.post("/compare")
def compare_wishlist_items(body: CompareBody, user_id: str = Depends(get_user_id)):
    conn = get_connection()
    try:
        wl_ids = {i.product_id for i in wishlist_repo.list_wishlist(conn, user_id)}
        for pid in body.product_ids:
            if pid not in wl_ids:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product {pid} must be on your Wishlist to compare",
                )
        return compare_service.compare_products(
            conn,
            body.product_ids,
            user_id,
            need=body.need,
            tradeoff_priority=body.tradeoff_priority,
            user_confidence=body.user_confidence,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        conn.close()


@router.post("/shortlist")
def shortlist_wishlist_items(body: ShortlistBody, user_id: str = Depends(get_user_id)):
    conn = get_connection()
    try:
        wl_ids = {i.product_id for i in wishlist_repo.list_wishlist(conn, user_id)}
        for pid in body.product_ids:
            if pid not in wl_ids:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product {pid} must be on your Wishlist to shortlist",
                )
        return shortlist_service.shortlist_products(
            conn,
            body.product_ids,
            user_id,
            need=body.need,
            tradeoff_priority=body.tradeoff_priority,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        conn.close()


@router.post("")
def add_to_wishlist(body: WishlistAddBody, user_id: str = Depends(get_user_id)):
    conn = get_connection()
    try:
        item = wishlist_repo.add_to_wishlist(
            conn, user_id, body.product_id, body.occasion, body.size
        )
        if not item:
            raise HTTPException(status_code=404, detail="Product not found")
        return item
    finally:
        conn.close()


@router.delete("/{product_id}", status_code=204)
def remove_from_wishlist(
    product_id: str = Path(..., pattern=r"^P\d+$"),
    user_id: str = Depends(get_user_id),
):
    conn = get_connection()
    try:
        removed = wishlist_repo.remove_from_wishlist(conn, user_id, product_id)
        if not removed:
            raise HTTPException(status_code=404, detail="Wishlist item not found")
    finally:
        conn.close()
