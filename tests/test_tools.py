
from refund_war_room.tools import ToolRegistry


def test_read_only_sql_query():
    tools = ToolRegistry()
    result = tools.sql_read_only_query(
        "SELECT order_id, status FROM refunds LIMIT 2"
    )
    assert result["row_count"] == 2
    assert result["columns"] == ["order_id", "status"]


def test_order_details():
    tools = ToolRegistry()
    result = tools.get_order_details("ORD-1001")
    assert result["found"] is True


def test_refund_status():
    tools = ToolRegistry()
    result = tools.get_refund_status("ORD-1001")
    assert result["count"] >= 1


def test_seller_details():
    tools = ToolRegistry()
    result = tools.get_seller_details("SELLER-101")
    assert result["found"] is True


def test_warehouse_notes():
    tools = ToolRegistry()
    result = tools.get_warehouse_notes("ORD-1001")
    assert result["count"] >= 1


def test_policy_lookup():
    tools = ToolRegistry()
    result = tools.get_policy("2026-10-24")
    assert result["found"] is True


def test_search_docs():
    tools = ToolRegistry()
    result = tools.search_docs("refund")
    assert "results" in result


def test_tool_call_budget():
    tools = ToolRegistry(max_tool_calls=1)
    tools.get_order_details("ORD-1001")

    import pytest
    with pytest.raises(Exception):
        tools.get_refund_status("ORD-1001")
