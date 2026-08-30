from fastapi import APIRouter, Depends, HTTPException

from backend.api.deps import get_user_id
from backend.db.session import get_connection
from backend.services import checkout_service

router = APIRouter(prefix="/api/checkout", tags=["checkout"])


@router.post("")
def mock_checkout(user_id: str = Depends(get_user_id)):
    conn = get_connection()
    try:
        return checkout_service.checkout(conn, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        conn.close()
