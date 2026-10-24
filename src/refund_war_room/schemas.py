
from typing import Literal

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    """A piece of evidence supporting a refund decision."""

    source: str = Field(
        description="Where the evidence came from, such as a database table or policy document."
    )
    reference_id: str = Field(
        description="The ID of the order, refund, ticket, note, or policy document."
    )
    detail: str = Field(
        description="A concise factual statement supported by the source."
    )


class RefundDecision(BaseModel):
    """Structured output for a refund investigation."""

    order_id: str = Field(
        description="The order being investigated."
    )
    refund_id: str | None = Field(
        default=None,
        description="The associated refund ID, if available."
    )
    recommendation: Literal[
        "approve",
        "reject",
        "request_more_information",
        "escalate",
    ] = Field(
        description="The recommended next action. This is not an actual refund execution."
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the recommendation, between 0 and 1."
    )
    reasoning: str = Field(
        description="A concise explanation grounded in the available evidence."
    )
    evidence: list[EvidenceItem] = Field(
        default_factory=list,
        description="Evidence supporting the recommendation."
    )
    missing_information: list[str] = Field(
        default_factory=list,
        description="Facts that must be checked before a decision can be finalized."
    )
    policy_document_id: str | None = Field(
        default=None,
        description="The authoritative policy document used, if established."
    )
    requires_human_review: bool = Field(
        default=True,
        description="Whether a human must review the recommendation."
    )
