
from refund_war_room.schemas import EvidenceItem, RefundDecision
from refund_war_room.verifier import verify_refund_decision


def make_decision(**overrides):
    data = {
        "order_id": "ORD-1001",
        "refund_id": "REF-2001",
        "recommendation": "approve",
        "confidence": 0.9,
        "reasoning": "The decision is supported by the available evidence.",
        "evidence": [
            EvidenceItem(
                source="refunds",
                reference_id="REF-2001",
                detail="Refund request is pending.",
            )
        ],
        "missing_information": [],
        "policy_document_id": "POL-002",
        "requires_human_review": True,
    }
    data.update(overrides)
    return RefundDecision(**data)


def test_valid_decision_passes_verification():
    decision = make_decision()

    result = verify_refund_decision(
        decision,
        authoritative_policy_id="POL-002",
        known_evidence_ids={"REF-2001"},
    )

    assert result.approved_for_review is True
    assert result.reasons == []


def test_policy_conflict_blocks_verification():
    result = verify_refund_decision(
        make_decision(),
        authoritative_policy_id="POL-002",
        known_evidence_ids={"REF-2001"},
        policy_conflict=True,
    )

    assert result.approved_for_review is False
    assert any("Conflicting policy" in reason for reason in result.reasons)


def test_unknown_evidence_blocks_verification():
    result = verify_refund_decision(
        make_decision(),
        authoritative_policy_id="POL-002",
        known_evidence_ids=set(),
    )

    assert result.approved_for_review is False
    assert any("Unverified evidence" in reason for reason in result.reasons)


def test_missing_policy_blocks_approval():
    result = verify_refund_decision(
        make_decision(),
        authoritative_policy_id=None,
        known_evidence_ids={"REF-2001"},
    )

    assert result.approved_for_review is False


def test_missing_information_blocks_definitive_decision():
    result = verify_refund_decision(
        make_decision(missing_information=["Final warehouse inspection"]),
        authoritative_policy_id="POL-002",
        known_evidence_ids={"REF-2001"},
    )

    assert result.approved_for_review is False


def test_low_confidence_requires_review():
    result = verify_refund_decision(
        make_decision(confidence=0.3),
        authoritative_policy_id="POL-002",
        known_evidence_ids={"REF-2001"},
    )

    assert result.approved_for_review is False
    assert any("Confidence" in reason for reason in result.reasons)


def test_verifier_does_not_execute_refund():
    decision = make_decision()

    result = verify_refund_decision(
        decision,
        authoritative_policy_id="POL-002",
        known_evidence_ids={"REF-2001"},
    )

    assert result.decision.recommendation == "approve"
    assert result.decision.requires_human_review is True
