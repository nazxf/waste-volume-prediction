"""
SQLite storage helpers for ESP32 smart-bin readings.
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "iot_readings.db"


def get_bin_status(fill_level: float) -> str:
    """Convert a fill percentage into a simple operational status."""
    if fill_level >= 90:
        return "full"
    if fill_level >= 70:
        return "high"
    if fill_level >= 40:
        return "medium"
    return "low"


def _connect(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    # timeout makes writers wait for a lock instead of failing instantly, and
    # WAL mode lets reads run concurrently with a writer. Together these avoid
    # "database is locked" errors when several ESP32 devices post at once.
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def init_iot_db(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Create the readings table if it does not exist."""
    with _connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bin_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bin_id TEXT NOT NULL,
                device_id TEXT NOT NULL,
                fill_level REAL NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_bin_readings_created_at
            ON bin_readings(created_at DESC)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_bin_readings_bin_id_created_at
            ON bin_readings(bin_id, created_at DESC)
            """
        )


def save_bin_reading(
    bin_id: str,
    device_id: str,
    fill_level: float,
    db_path: Path = DEFAULT_DB_PATH,
) -> Dict[str, Any]:
    """Persist one ESP32 bin reading and return the saved row."""
    init_iot_db(db_path)
    status = get_bin_status(fill_level)
    created_at = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    with _connect(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO bin_readings (bin_id, device_id, fill_level, status, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (bin_id, device_id, fill_level, status, created_at),
        )
        reading_id = cursor.lastrowid

    return {
        "id": reading_id,
        "bin_id": bin_id,
        "device_id": device_id,
        "fill_level": fill_level,
        "status": status,
        "created_at": created_at,
    }


def get_latest_readings(
    limit: int = 20,
    db_path: Path = DEFAULT_DB_PATH,
) -> List[Dict[str, Any]]:
    """Return the newest readings across all bins."""
    init_iot_db(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT id, bin_id, device_id, fill_level, status, created_at
            FROM bin_readings
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_latest_bin_reading(
    bin_id: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> Optional[Dict[str, Any]]:
    """Return the newest reading for one bin."""
    init_iot_db(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT id, bin_id, device_id, fill_level, status, created_at
            FROM bin_readings
            WHERE bin_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """,
            (bin_id,),
        ).fetchone()
    return dict(row) if row else None
