
import re


ALLOWED_SQL_TABLES = {
    "orders",
    "refunds",
    "sellers",
    "support_tickets",
    "warehouse_notes",
    "policy_documents",
}


BLOCKED_SQL_KEYWORDS = {
    "insert", "update", "delete", "drop", "alter",
    "create", "replace", "attach", "detach",
    "pragma", "vacuum", "reindex", "analyze",
}


def validate_read_only_sql(query: str) -> tuple[bool, str]:
    """Perform preliminary validation before SQLite authorization."""

    if not isinstance(query, str) or not query.strip():
        return False, "Query must be a non-empty string."

    query = query.strip()

    if len(query) > 5000:
        return False, "Query exceeds the maximum permitted length."

    if "--" in query or "/*" in query or "*/" in query:
        return False, "SQL comments are not permitted."

    if not re.match(r"^(SELECT|WITH)\b", query, re.IGNORECASE):
        return False, "Only SELECT or WITH queries are permitted."

    without_trailing_semicolon = query.rstrip().rstrip(";").rstrip()
    if ";" in without_trailing_semicolon:
        return False, "Multiple SQL statements are not permitted."

    tokens = re.findall(r"\b[A-Za-z_]+\b", query.lower())

    if any(token in BLOCKED_SQL_KEYWORDS for token in tokens):
        return False, "A prohibited SQL keyword was detected."

    return True, "Query passed preliminary validation."


def validate_seller_message(
    seller_id: str,
    message: str,
    authorized: bool,
    allowed_seller_ids: set[str],
) -> tuple[bool, str]:
    """Validate a simulated outbound seller message."""

    if not authorized:
        return False, "Explicit authorization is required."

    if seller_id not in allowed_seller_ids:
        return False, "Seller is not in the allowed seller list."

    if not isinstance(message, str) or not message.strip():
        return False, "Message cannot be empty."

    if len(message) > 1000:
        return False, "Message exceeds the 1000-character limit."

    return True, "Message passed validation."
