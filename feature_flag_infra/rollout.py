from __future__ import annotations

import hashlib
from typing import Any


def get_user_identifier(user: Any) -> str | None:
    if user is None:
        return None

    user_id = getattr(user, "id", None) or getattr(user, "pk", None)

    if user_id is None:
        return None

    return str(user_id)


def is_user_in_rollout(flag: str, user: Any, percentage: int) -> bool:
    user_id = get_user_identifier(user)

    if user_id is None:
        return False

    bucket = int(
        hashlib.md5(f"{flag}:{user_id}".encode()).hexdigest(),
        16,
    ) % 100

    return bucket < percentage