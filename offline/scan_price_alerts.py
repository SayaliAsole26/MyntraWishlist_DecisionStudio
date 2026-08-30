"""Scan wishlist items for price drops vs saved_price."""

from backend.db.schema import ensure_schema
from backend.db.session import get_connection
from backend.services.alert_service import scan_price_alerts


def main() -> int:
    conn = get_connection()
    try:
        ensure_schema(conn)
        result = scan_price_alerts(conn)
    finally:
        conn.close()
    print(f"price-drop alerts created: {result['alerts_created']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
