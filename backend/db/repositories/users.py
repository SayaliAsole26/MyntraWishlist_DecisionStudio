import sqlite3

from backend.db.util import dump_json_list, parse_json_list
from backend.models import ProfileOut, ProfileUpdate


def get_profile(conn: sqlite3.Connection, user_id: str) -> ProfileOut | None:
    row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if not row:
        return None
    return ProfileOut(
        user_id=row["user_id"],
        display_name=row["display_name"],
        size=row["size"],
        price_min=row["price_min"],
        price_max=row["price_max"],
        occasions=parse_json_list(row["occasions"]),
        priorities=parse_json_list(row["priorities"]),
    )


def update_profile(
    conn: sqlite3.Connection, user_id: str, data: ProfileUpdate
) -> ProfileOut | None:
    current = get_profile(conn, user_id)
    if not current:
        return None

    if (
        data.price_min is not None
        and data.price_max is not None
        and data.price_max < data.price_min
    ):
        raise ValueError("price_max must be >= price_min")

    display_name = data.display_name if data.display_name is not None else current.display_name
    size = data.size if data.size is not None else current.size
    price_min = data.price_min if data.price_min is not None else current.price_min
    price_max = data.price_max if data.price_max is not None else current.price_max
    occasions = data.occasions if data.occasions is not None else current.occasions
    priorities = data.priorities if data.priorities is not None else current.priorities

    conn.execute(
        """
        UPDATE users
        SET display_name = ?, size = ?, price_min = ?, price_max = ?,
            occasions = ?, priorities = ?
        WHERE user_id = ?
        """,
        (
            display_name,
            size,
            price_min,
            price_max,
            dump_json_list(occasions),
            dump_json_list(priorities),
            user_id,
        ),
    )
    conn.commit()
    return get_profile(conn, user_id)


def clear_profile(conn: sqlite3.Connection, user_id: str) -> ProfileOut | None:
    if not get_profile(conn, user_id):
        return None

    conn.execute(
        """
        UPDATE users
        SET display_name = NULL, size = NULL, price_min = NULL, price_max = NULL,
            occasions = ?, priorities = ?
        WHERE user_id = ?
        """,
        (dump_json_list([]), dump_json_list([]), user_id),
    )
    conn.commit()
    return get_profile(conn, user_id)
