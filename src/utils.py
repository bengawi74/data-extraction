import re
from typing import Optional

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email: Optional[str]) -> bool:
    """Basic email sanity check."""
    if not email or not isinstance(email, str):
        return False
    return bool(_EMAIL_RE.match(email.strip()))


def completion_rate(total: int, completed: int) -> float:
    """Completed / total (safe for zero)."""
    if total and total > 0:
        return round(completed / total, 2)
    return 0.0


def amount_bucket(amount: int) -> str:
    """Buckets that match your dataset: <100 low, 100–149 mid, >=150 high."""
    if amount >= 150:
        return "high"
    if amount >= 100:
        return "mid"
    return "low"
