import pytest

from src.utils import amount_bucket, completion_rate, is_valid_email


@pytest.mark.parametrize(
    "email,expected",
    [
        ("alice@example.com", True),
        ("bob.smith@sub.domain.org", True),
        ("bad@", False),
        ("@nope.com", False),
        ("", False),
        (None, False),
        (" spaced @out.com ", False),
    ],
)
def test_is_valid_email(email, expected):
    assert is_valid_email(email) is expected


@pytest.mark.parametrize(
    "total,done,expected",
    [
        (20, 11, 0.55),
        (20, 8, 0.40),
        (0, 7, 0.0),
        (5, 0, 0.0),
    ],
)
def test_completion_rate(total, done, expected):
    assert completion_rate(total, done) == expected


@pytest.mark.parametrize(
    "amt,bucket",
    [
        (90, "low"),
        (100, "mid"),
        (149, "mid"),
        (150, "high"),
        (999, "high"),
    ],
)
def test_amount_bucket(amt, bucket):
    assert amount_bucket(amt) == bucket
