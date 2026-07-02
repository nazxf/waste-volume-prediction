"""
Export utilities for Phase 2 prediction results.
"""
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages


def predictions_to_dataframe(daily_predictions: List[Dict]) -> pd.DataFrame:
    """Convert daily prediction dictionaries to a normalized DataFrame."""
    df = pd.DataFrame(daily_predictions)
    if "confidence_interval" in df.columns:
        intervals = pd.json_normalize(df["confidence_interval"]).add_prefix("interval_")
        df = pd.concat([df.drop(columns=["confidence_interval"]), intervals], axis=1)
    if "anomaly" in df.columns:
        anomalies = pd.json_normalize(df["anomaly"]).add_prefix("anomaly_")
        df = pd.concat([df.drop(columns=["anomaly"]), anomalies], axis=1)
    return df


def export_predictions_to_excel(
    summary: Dict,
    daily_predictions: List[Dict],
    output_path: Optional[Union[str, Path]] = None
) -> bytes:
    """
    Export prediction summary and daily rows to an Excel workbook.
    """
    buffer = BytesIO()
    summary_df = pd.DataFrame([summary])
    predictions_df = predictions_to_dataframe(daily_predictions)

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        predictions_df.to_excel(writer, sheet_name="Daily Predictions", index=False)

    data = buffer.getvalue()
    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_bytes(data)

    return data


def export_predictions_to_pdf(
    summary: Dict,
    daily_predictions: List[Dict],
    output_path: Optional[Union[str, Path]] = None
) -> bytes:
    """
    Export prediction summary and daily rows to a compact PDF report.
    """
    buffer = BytesIO()
    predictions_df = predictions_to_dataframe(daily_predictions)
    display_df = predictions_df.head(30).copy()

    with PdfPages(buffer) as pdf:
        fig, ax = plt.subplots(figsize=(8.27, 11.69))
        ax.axis("off")
        ax.set_title("Waste Volume Prediction Report", fontsize=16, fontweight="bold", pad=20)

        summary_lines = [
            f"{key}: {value}" for key, value in summary.items()
        ]
        ax.text(
            0.02,
            0.95,
            "\n".join(summary_lines),
            transform=ax.transAxes,
            fontsize=10,
            va="top",
            family="monospace",
        )

        table_columns = [
            col for col in ["date", "day_name", "predicted_volume", "interval_lower_bound", "interval_upper_bound"]
            if col in display_df.columns
        ]
        table_df = display_df[table_columns].round(2) if table_columns else display_df

        table = ax.table(
            cellText=table_df.values,
            colLabels=table_df.columns,
            cellLoc="center",
            loc="lower center",
            bbox=[0.02, 0.05, 0.96, 0.65],
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.2)
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

    data = buffer.getvalue()
    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_bytes(data)

    return data


def save_prediction_exports(
    summary: Dict,
    daily_predictions: List[Dict],
    output_dir: Union[str, Path],
    filename_prefix: str = "prediction"
) -> Tuple[Path, Path]:
    """Save Excel and PDF exports to an output directory."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    excel_path = output_dir / f"{filename_prefix}.xlsx"
    pdf_path = output_dir / f"{filename_prefix}.pdf"

    export_predictions_to_excel(summary, daily_predictions, excel_path)
    export_predictions_to_pdf(summary, daily_predictions, pdf_path)

    return excel_path, pdf_path
