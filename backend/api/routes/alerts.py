from fastapi import APIRouter, Depends, HTTPException

from backend.api.deps import get_user_id
from backend.db.session import get_connection
from backend.services import alert_service

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.patch("/{alert_id}/dismiss")
def dismiss_alert(alert_id: str, user_id: str = Depends(get_user_id)):
    conn = get_connection()
    try:
        dismissed = alert_service.dismiss_alert(conn, user_id, alert_id)
        if not dismissed:
            raise HTTPException(status_code=404, detail="Alert not found or already dismissed")
        return {"alert_id": alert_id, "dismissed": True}
    finally:
        conn.close()
