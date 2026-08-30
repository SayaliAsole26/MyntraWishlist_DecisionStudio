import json
from typing import Any


def parse_json_list(value: str | None) -> list[Any]:
    if not value:
        return []
    try:
        data = json.loads(value)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def dump_json_list(items: list[Any] | None) -> str:
    return json.dumps(items or [])
