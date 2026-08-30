from fastapi import Header, HTTPException, Query

ALLOWED_USERS = {"U001"}
DEFAULT_USER = "U001"


def get_user_id(
    user_id: str | None = Query(None),
    x_user_id: str | None = Header(None, alias="X-User-Id"),
) -> str:
    uid = user_id or x_user_id or DEFAULT_USER
    if uid not in ALLOWED_USERS:
        raise HTTPException(status_code=403, detail="Unknown user")
    return uid
