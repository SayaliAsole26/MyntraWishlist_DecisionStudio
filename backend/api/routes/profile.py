from fastapi import APIRouter, Depends, HTTPException

from backend.api.deps import get_user_id
from backend.db.repositories import users as user_repo
from backend.db.session import get_connection
from backend.models import ProfileUpdate

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("")
def get_profile(user_id: str = Depends(get_user_id)):
    conn = get_connection()
    try:
        profile = user_repo.get_profile(conn, user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")
        return profile
    finally:
        conn.close()


@router.patch("")
def update_profile(body: ProfileUpdate, user_id: str = Depends(get_user_id)):
    conn = get_connection()
    try:
        try:
            profile = user_repo.update_profile(conn, user_id, body)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")
        return profile
    finally:
        conn.close()


@router.post("/clear")
def clear_profile(user_id: str = Depends(get_user_id)):
    conn = get_connection()
    try:
        profile = user_repo.clear_profile(conn, user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")
        return profile
    finally:
        conn.close()
