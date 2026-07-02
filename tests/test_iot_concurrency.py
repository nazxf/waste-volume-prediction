"""
Concurrency test for IoT SQLite storage.

Simulates many ESP32 devices posting readings at the same time and checks
that no writes are lost or rejected with "database is locked".

Run: python -m pytest tests/test_iot_concurrency.py
"""
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from iot_storage import get_latest_readings, init_iot_db, save_bin_reading

N_DEVICES = 20
READINGS_PER_DEVICE = 25
EXPECTED_TOTAL = N_DEVICES * READINGS_PER_DEVICE


def _write_batch(db_path: Path, device_index: int):
    errors = []
    for i in range(READINGS_PER_DEVICE):
        try:
            save_bin_reading(
                bin_id=f"TPS-{device_index:03d}",
                device_id=f"ESP32-{device_index:03d}",
                fill_level=(i * 4) % 100,
                db_path=db_path,
            )
        except Exception as e:  # noqa: BLE001 - we want to surface any failure
            errors.append(repr(e))
    return errors


def _run_concurrency_check() -> tuple[list[str], int]:
    # ignore_cleanup_errors: on Windows the WAL side files may stay briefly
    # locked after the last connection closes; that is harmless for the test.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        db_path = Path(tmp) / "iot_test.db"
        init_iot_db(db_path)

        all_errors = []
        with ThreadPoolExecutor(max_workers=N_DEVICES) as pool:
            futures = [
                pool.submit(_write_batch, db_path, d) for d in range(N_DEVICES)
            ]
            for fut in as_completed(futures):
                all_errors.extend(fut.result())

        # Count what actually landed in the database.
        stored = get_latest_readings(limit=EXPECTED_TOTAL + 10, db_path=db_path)
        stored_count = len(stored)

    return all_errors, stored_count


def test_concurrent_iot_writes_are_not_lost():
    all_errors, stored_count = _run_concurrency_check()

    assert all_errors == []
    assert stored_count == EXPECTED_TOTAL


def main() -> int:
    all_errors, stored_count = _run_concurrency_check()

    print(f"Devices            : {N_DEVICES}")
    print(f"Per device         : {READINGS_PER_DEVICE}")
    print(f"Expected writes    : {EXPECTED_TOTAL}")
    print(f"Stored in database : {stored_count}")
    print(f"Write errors       : {len(all_errors)}")

    ok = not all_errors and stored_count == EXPECTED_TOTAL
    if ok:
        print("\n[PASS] All concurrent writes succeeded with no lost rows.")
        return 0

    if all_errors:
        print("\n[FAIL] Write errors occurred:")
        for err in all_errors[:10]:
            print(f"  - {err}")
    if stored_count != EXPECTED_TOTAL:
        print(f"\n[FAIL] Lost rows: expected {EXPECTED_TOTAL}, got {stored_count}.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
