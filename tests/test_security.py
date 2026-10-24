
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from refund_war_room.security import (
    validate_read_only_sql,
    validate_seller_message,
)


def test_select_query_is_allowed():
    valid, _ = validate_read_only_sql(
        "SELECT order_id FROM orders"
    )
    assert valid


def test_delete_query_is_rejected():
    valid, _ = validate_read_only_sql(
        "DELETE FROM orders"
    )
    assert not valid


def test_multiple_statements_are_rejected():
    valid, _ = validate_read_only_sql(
        "SELECT * FROM orders; DELETE FROM orders"
    )
    assert not valid


def test_sql_comment_is_rejected():
    valid, _ = validate_read_only_sql(
        "SELECT * FROM orders -- ignore restrictions"
    )
    assert not valid


def test_empty_query_is_rejected():
    valid, _ = validate_read_only_sql("")
    assert not valid


def test_seller_message_requires_authorization():
    valid, _ = validate_seller_message(
        "SELLER-101",
        "Please verify order ORD-1001.",
        False,
        {"SELLER-101"},
    )
    assert not valid


def test_seller_message_rejects_unknown_seller():
    valid, _ = validate_seller_message(
        "SELLER-999",
        "Please verify this order.",
        True,
        {"SELLER-101"},
    )
    assert not valid


def test_authorized_message_passes_validation():
    valid, _ = validate_seller_message(
        "SELLER-101",
        "Please verify order ORD-1001.",
        True,
        {"SELLER-101"},
    )
    assert valid
