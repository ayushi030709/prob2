
from datetime import date

from refund_war_room.schemas import EvidenceItem, RefundDecision
from refund_war_room.tools import ToolRegistry
from refund_war_room.verifier import (
    VerificationResult,
    verify_refund_decision,
)


class RefundInvestigationAgent:
    """Coordinate refund investigation tools and decision verification."""

    def __init__(self, tools: ToolRegistry | None = None):
        self.tools = tools or ToolRegistry()

    def investigate(self, order_id: str) -> dict:
        """Gather evidence and produce a decision for human review."""

        if not isinstance(order_id, str) or not order_id.strip():
            raise ValueError("A valid order ID is required.")

        order_id = order_id.strip()

        order_result = self.tools.get_order_details(order_id)

        if not order_result.get("found"):
            return {
                "status": "not_found",
                "order_id": order_id,
                "message": "No matching order was found.",
            }

        refund_result = self.tools.get_refund_status(order_id)
        warehouse_result = self.tools.get_warehouse_notes(order_id)

        order = order_result["order"]
        refunds = refund_result.get("refunds", [])
        warehouse_notes = warehouse_result.get("notes", [])

        evidence = [
            EvidenceItem(
                source="orders",
                reference_id=order_id,
                detail=f"Order belongs to seller {order['seller_id']}.",
            )
        ]

        for refund in refunds:
            evidence.append(
                EvidenceItem(
                    source="refunds",
                    reference_id=refund["refund_id"],
                    detail=(
                        f"Refund status is {refund['status']}; "
                        f"reason: {refund['reason']}."
                    ),
                )
            )

        for note in warehouse_notes:
            evidence.append(
                EvidenceItem(
                    source="warehouse_notes",
                    reference_id=note["note_id"],
                    detail=note["note_text"],
                )
            )

        # Retrieve the policy applicable on the investigation date.
        policy_result = self.tools.get_policy(date.today().isoformat())

        policy_id = None
        policy_conflict = bool(
            policy_result.get("conflict")
            or policy_result.get("conflicting_document_ids")
        )

        if policy_result.get("found") and not policy_conflict:
            policy = policy_result["policy"]
            policy_id = policy["document_id"]

            evidence.append(
                EvidenceItem(
                    source="policy_documents",
                    reference_id=policy_id,
                    detail=policy["document_text"],
                )
            )

        # Never make a definitive recommendation without reliable policy
        # evidence. A refund record alone does not prove eligibility.
        if policy_conflict or not policy_id:
            recommendation = "escalate"
            missing_information = [
                "A verified, authoritative refund policy"
            ]
        elif not refunds:
            recommendation = "request_more_information"
            missing_information = [
                "A refund record for this order"
            ]
        else:
            recommendation = "request_more_information"
            missing_information = [
                "Complete refund eligibility assessment",
                "Confirmation of required return or warehouse evidence",
            ]

        decision = RefundDecision(
            order_id=order_id,
            refund_id=refunds[0]["refund_id"] if refunds else None,
            recommendation=recommendation,
            confidence=0.8 if policy_id and not policy_conflict else 0.3,
            reasoning=(
                "The investigation gathered order, refund, warehouse, "
                "and policy evidence. A definitive refund decision is "
                "not made by this workflow. Human review is required."
            ),
            evidence=evidence,
            missing_information=missing_information,
            policy_document_id=policy_id,
            requires_human_review=True,
        )

        known_evidence_ids = {
            item.reference_id for item in evidence
        }

        verification: VerificationResult = verify_refund_decision(
            decision=decision,
            authoritative_policy_id=policy_id,
            known_evidence_ids=known_evidence_ids,
            policy_conflict=policy_conflict,
        )

        return {
            "status": (
                "verified_for_review"
                if verification.approved_for_review
                else "verification_failed"
            ),
            "order_id": order_id,
            "decision": decision.model_dump(),
            "verification": {
                "approved_for_review": verification.approved_for_review,
                "reasons": verification.reasons,
            },
            "tool_calls_used": self.tools.call_count,
        }
