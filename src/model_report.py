"""
Read-only model performance reporting for the dashboard API.

Parses the evaluation report and prediction metadata produced by training so a
browser client can render the same performance view the Streamlit app showed.
Nothing here trains or changes the model.
"""
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib


PROJECT_ROOT = Path(__file__).parent.parent
REPORT_PATH = PROJECT_ROOT / "reports" / "evaluation_report.md"
METADATA_PATH = PROJECT_ROOT / "models" / "prediction_metadata.pkl"
FEATURE_IMPORTANCE_IMG = PROJECT_ROOT / "reports" / "feature_importance.png"
PREDICTION_COMPARISON_IMG = PROJECT_ROOT / "reports" / "prediction_comparison.png"


def _parse_markdown_table(markdown: str, header_contains: str) -> List[List[str]]:
    """Return data rows (as cell lists) of the first table whose header matches.

    A header is only recognised when it is a pipe row immediately followed by a
    separator row (``|---|---|``), so a data cell that happens to contain the
    search token does not trigger a false match.
    """
    lines = markdown.splitlines()

    def is_pipe_row(text: str) -> bool:
        return text.strip().startswith("|")

    def is_separator(text: str) -> bool:
        cells = [c.strip() for c in text.strip().strip("|").split("|")]
        return bool(cells) and all(set(c) <= {"-", ":", " "} and "-" in c for c in cells)

    rows: List[List[str]] = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not is_pipe_row(stripped):
            continue
        if header_contains.lower() not in stripped.lower():
            continue
        if i + 1 >= len(lines) or not is_separator(lines[i + 1]):
            continue  # token appeared in a non-header row
        # Collect data rows after the separator.
        for data_line in lines[i + 2:]:
            if not is_pipe_row(data_line):
                break
            cells = [c.strip() for c in data_line.strip().strip("|").split("|")]
            rows.append(cells)
        break
    return rows


def _to_float(text: str) -> Optional[float]:
    match = re.search(r"-?\d+\.?\d*", text)
    return float(match.group()) if match else None


def _feature_importance(markdown: str) -> List[Dict[str, Any]]:
    rows = _parse_markdown_table(markdown, "Importance")
    items = []
    for cells in rows:
        if len(cells) >= 3:
            items.append(
                {
                    "rank": int(_to_float(cells[0]) or 0),
                    "feature": cells[1],
                    "importance": _to_float(cells[2]),
                }
            )
    return items


def _model_comparison(markdown: str) -> List[Dict[str, Any]]:
    rows = _parse_markdown_table(markdown, "RMSE")
    items = []
    for cells in rows:
        if len(cells) >= 5:
            name = cells[0]
            items.append(
                {
                    "model": name.replace("*", "").strip(),
                    "is_best": "*" in name,
                    "mae": _to_float(cells[1]),
                    "rmse": _to_float(cells[2]),
                    "r2": _to_float(cells[3]),
                    "mape": _to_float(cells[4]),
                }
            )
    return items


def get_model_performance() -> Dict[str, Any]:
    """Bundle the evaluation report, metadata, and parsed tables for the client."""
    report_markdown = ""
    if REPORT_PATH.exists():
        report_markdown = REPORT_PATH.read_text(encoding="utf-8")

    metadata: Dict[str, Any] = {}
    if METADATA_PATH.exists():
        metadata = joblib.load(METADATA_PATH)

    return {
        "available": bool(report_markdown) or bool(metadata),
        "report_markdown": report_markdown,
        "metadata": metadata,
        "feature_importance": _feature_importance(report_markdown),
        "model_comparison": _model_comparison(report_markdown),
        "has_feature_importance_image": FEATURE_IMPORTANCE_IMG.exists(),
        "has_prediction_comparison_image": PREDICTION_COMPARISON_IMG.exists(),
    }
