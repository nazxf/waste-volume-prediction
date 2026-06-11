"""
Automated retraining entrypoint for Phase 2.
"""
import argparse
from datetime import datetime
from pathlib import Path
import shutil
import sys

import pandas as pd

sys.path.append(str(Path(__file__).parent))

from data_generator import generate_waste_dataset
from preprocess import validate_dataset
from train_model import main as train_main
from utils import ensure_dir


def append_retraining_log(project_root: Path, status: str, reason: str, data_path: str) -> Path:
    """Append a retraining event to reports/retraining_log.csv."""
    reports_dir = ensure_dir(project_root / "reports")
    log_path = reports_dir / "retraining_log.csv"
    row = {
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "status": status,
        "reason": reason,
        "data_path": data_path,
    }

    if log_path.exists():
        log_df = pd.read_csv(log_path)
        log_df = pd.concat([log_df, pd.DataFrame([row])], ignore_index=True)
    else:
        log_df = pd.DataFrame([row])

    log_df.to_csv(log_path, index=False)
    return log_path


def prepare_training_data(project_root: Path, data_path: str = None, generate_if_missing: bool = True) -> Path:
    """Validate and place training data at data/raw/waste_dataset.csv."""
    target_path = project_root / "data" / "raw" / "waste_dataset.csv"
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if data_path:
        source_path = Path(data_path)
        df = pd.read_csv(source_path)
        validate_dataset(df)
        shutil.copyfile(source_path, target_path)
        return target_path

    if generate_if_missing and not target_path.exists():
        generate_waste_dataset(output_path=str(target_path))

    if not target_path.exists():
        raise FileNotFoundError(
            f"Training dataset not found at {target_path}. Provide --data-path or allow generation."
        )

    return target_path


def run_retraining(data_path: str = None, reason: str = "scheduled", generate_if_missing: bool = True) -> Path:
    """Run the automated retraining pipeline and return the log path."""
    project_root = Path(__file__).parent.parent
    prepared_path = prepare_training_data(project_root, data_path, generate_if_missing)

    try:
        train_main()
        return append_retraining_log(project_root, "success", reason, str(prepared_path))
    except Exception:
        append_retraining_log(project_root, "failed", reason, str(prepared_path))
        raise


def parse_args():
    parser = argparse.ArgumentParser(description="Run automated model retraining.")
    parser.add_argument("--data-path", help="Optional CSV file to validate and use for retraining.")
    parser.add_argument("--reason", default="manual", help="Reason stored in retraining log.")
    parser.add_argument(
        "--no-generate",
        action="store_true",
        help="Do not auto-generate synthetic data when no dataset exists.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    log_file = run_retraining(
        data_path=args.data_path,
        reason=args.reason,
        generate_if_missing=not args.no_generate,
    )
    print(f"[OK] Retraining completed. Log updated at {log_file}")

