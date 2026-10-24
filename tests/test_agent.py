
from refund_war_room.agent import RefundInvestigationAgent


def test_agent_investigates_existing_order():
    agent = RefundInvestigationAgent()

    result = agent.investigate("ORD-1001")

    assert result["status"] == "verified_for_review"
    assert result["order_id"] == "ORD-1001"
    assert result["decision"]["recommendation"] == "request_more_information"
    assert result["verification"]["approved_for_review"] is True


def test_agent_includes_evidence():
    agent = RefundInvestigationAgent()

    result = agent.investigate("ORD-1001")

    sources = {
        item["source"] for item in result["decision"]["evidence"]
    }

    assert "orders" in sources
    assert "refunds" in sources
    assert "warehouse_notes" in sources
    assert "policy_documents" in sources


def test_agent_requires_human_review():
    agent = RefundInvestigationAgent()

    result = agent.investigate("ORD-1001")

    assert result["decision"]["requires_human_review"] is True


def test_agent_handles_unknown_order():
    agent = RefundInvestigationAgent()

    result = agent.investigate("ORD-9999")

    assert result["status"] == "not_found"
    assert result["order_id"] == "ORD-9999"


def test_agent_rejects_empty_order_id():
    import pytest

    agent = RefundInvestigationAgent()

    with pytest.raises(ValueError):
        agent.investigate("  ")


def test_agent_respects_tool_call_budget():
    from refund_war_room.tools import ToolRegistry

    tools = ToolRegistry(max_tool_calls=3)
    agent = RefundInvestigationAgent(tools=tools)

    import pytest
    from refund_war_room.tools import ToolBudgetExceeded

    with pytest.raises(ToolBudgetExceeded):
        agent.investigate("ORD-1001")
