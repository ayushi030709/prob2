
from pathlib import Path

# Project root: .../prob2
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
DATABASE_PATH = DATA_DIR / "refund_war_room.db"

MAX_TOOL_CALLS = 8

DATA_DIR.mkdir(parents=True, exist_ok=True)
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
