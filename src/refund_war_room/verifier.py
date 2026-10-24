
from dataclasses import dataclass, field

from refund_war_room.schemas import RefundDecision


@dataclass
class VerificationResult:
    """Outcome of checking a proposed refund decision."""

    approved_for_review: bool
    reasons: list[str] = field(default_factory=list)
    decision: RefundDecision | None = None


def verify_refund_decision(
    decision: RefundDecision,
    authoritative_policy_id: str | None,
    known_evidence_ids: set[str],
    policy_conflict: bool = False,
) -> VerificationResult:
    """
    Check a proposed decision against known evidence and policy.

    This function does not approve or execute an actual refund.
    It determines whether the recommendation is sufficiently supported
    to be passed to a human reviewer.
    """
    reasons: list[str] = []

    # A policy conflict means we cannot safely rely on one policy.
    if policy_conflict:
        reasons.append("Conflicting policy documents require human review.")

    # A policy-dependent decision needs an identified authoritative policy.
    if decision.recommendation in {"approve", "reject"}:
        if not authoritative_policy_id:
            reasons.append(
                "No authoritative policy was established for the decision."
            )
        elif decision.policy_document_id != authoritative_policy_id:
            reasons.append(
                "The decision does not reference the authoritative policy."
            )

    # Every cited evidence item must be present in the known evidence set.
    for item in decision.evidence:
        if item.reference_id not in known_evidence_ids:
            reasons.append(
                f"Unverified evidence reference: {item.reference_id}"
            )

    # An approval or rejection should not be finalized when facts are missing.
    if (
        decision.recommendation in {"approve", "reject"}
        and decision.missing_information
    ):
        reasons.append(
            "Required information is missing; a definitive recommendation "
            "is not sufficiently supported."
        )

    # Low confidence requires a cautious outcome.
    if decision.confidence < 0.5:
        reasons.append(
            "Confidence is below 0.5; the recommendation needs further review."
        )

    # Escalation and requests for information are cautious outcomes.
    # They can still be passed to a human reviewer.
    passed = not reasons

    if not passed:
        decision.requires_human_review = True

    return VerificationResult(
        approved_for_review=passed,
        reasons=reasons,
        decision=decision,
    )
