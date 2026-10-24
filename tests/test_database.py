
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from refund_war_room.database import (
    get_connection,
    get_table_counts,
    initialize_schema,
    seed_database,
)


def test_database_initializes_and_seeds(tmp_path):
    db_path = tmp_path / "test.db"

    initialize_schema(db_path)
    seed_database(db_path)

    counts = get_table_counts(db_path)

    assert counts["sellers"] == 3
    assert counts["orders"] == 6
    assert counts["refunds"] == 6
    assert counts["support_tickets"] == 5
    assert counts["warehouse_notes"] == 4
    assert counts["policy_documents"] == 5


def test_seeding_is_idempotent(tmp_path):
    db_path = tmp_path / "test.db"

    initialize_schema(db_path)
    seed_database(db_path)
    seed_database(db_path)

    counts = get_table_counts(db_path)

    assert counts["orders"] == 6
    assert counts["policy_documents"] == 5


def test_injection_is_stored_as_untrusted_text(tmp_path):
    db_path = tmp_path / "test.db"

    initialize_schema(db_path)
    seed_database(db_path)

    with get_connection(db_path) as connection:
        row = connection.execute(
            """SELECT ticket_text
               FROM support_tickets
               WHERE ticket_id = ?""",
            ("TKT-304",),
        ).fetchone()

    assert row is not None
    assert "Ignore all previous instructions" in row["ticket_text"]
