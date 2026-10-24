
import sys
from pathlib import Path

# Allow Python to find the src package when this script runs.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from refund_war_room.database import (
    initialize_schema,
    seed_database,
    get_table_counts,
)


def main() -> None:
    initialize_schema()
    seed_database()

    print("\nRefund War Room database initialized.")
    print("\nSeeded record counts:")

    for table, count in get_table_counts().items():
        print(f"  {table}: {count}")

    print("\nDatabase initialization complete.")


if __name__ == "__main__":
    main()
