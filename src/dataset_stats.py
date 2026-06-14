"""
Read-only dataset statistics for the dashboard API.

These helpers read the same training CSV that the Streamlit dashboard used and
expose summary statistics over HTTP. They never train or mutate the model; they
only describe the historical dataset so a browser client can render the same
charts the in-process Streamlit app produced.
"""
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_DATASET_PATH = PROJECT_ROOT / "data" / "raw" / "waste_dataset.csv"

# Indonesian weekday labels, Monday-first to match the source dashboard.
_DAY_LABELS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

_CORRELATION_COLUMNS = [
    "temperature",
    "rainfall",
    "humidity",
    "holiday",
    "weekend",
    "population_density",
    "event_level",
    "waste_volume",
]


class DatasetNotFoundError(FileNotFoundError):
    """Raised when the training dataset CSV is missing."""


def _load_raw(path: Path, mtime: float) -> pd.DataFrame:
    """Load and parse the dataset. `mtime` busts the cache when the file changes."""
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


@lru_cache(maxsize=4)
def _cached_load(path_str: str, mtime: float) -> pd.DataFrame:
    return _load_raw(Path(path_str), mtime)


def load_dataset(path: Path = DEFAULT_DATASET_PATH) -> pd.DataFrame:
    """Return the dataset as a DataFrame, cached on the file's modified time."""
    if not path.exists():
        raise DatasetNotFoundError(
            f"Dataset not found at {path}. Run 'python src/train_model.py' first."
        )
    return _cached_load(str(path), path.stat().st_mtime)


def get_overview(
    trend_days: int = 90, path: Path = DEFAULT_DATASET_PATH
) -> Dict[str, Any]:
    """Headline metrics plus a recent waste-volume trend for the home page."""
    df = load_dataset(path)
    volume = df["waste_volume"]

    recent = df.tail(trend_days)
    trend = [
        {"date": d.strftime("%Y-%m-%d"), "waste_volume": round(float(v), 2)}
        for d, v in zip(recent["date"], recent["waste_volume"])
    ]

    # Most recent feature row, used by the dashboard for a "quick prediction"
    # with realistic drivers (matching the Streamlit home page behaviour).
    last = df.iloc[-1]
    latest_features = {
        "temperature": float(last["temperature"]),
        "rainfall": float(last["rainfall"]),
        "humidity": float(last["humidity"]),
        "holiday": int(last["holiday"]),
        "weekend": int(last["weekend"]),
        "population_density": float(last["population_density"]),
        "event_level": int(last["event_level"]),
    }

    return {
        "total_days": int(len(df)),
        "average_daily": round(float(volume.mean()), 2),
        "max_volume": round(float(volume.max()), 2),
        "min_volume": round(float(volume.min()), 2),
        "total_volume": round(float(volume.sum()), 2),
        "date_start": df["date"].iloc[0].strftime("%Y-%m-%d"),
        "date_end": df["date"].iloc[-1].strftime("%Y-%m-%d"),
        "latest_features": latest_features,
        "trend": trend,
    }


def get_analysis(
    histogram_bins: int = 30, path: Path = DEFAULT_DATASET_PATH
) -> Dict[str, Any]:
    """Distribution, weekday averages, monthly trend, and correlation matrix."""
    df = load_dataset(path)

    # Volume distribution histogram.
    counts, edges = np.histogram(df["waste_volume"], bins=histogram_bins)
    distribution = [
        {
            "bin_start": round(float(edges[i]), 2),
            "bin_end": round(float(edges[i + 1]), 2),
            "count": int(counts[i]),
        }
        for i in range(len(counts))
    ]

    # Average volume per weekday (Monday-first).
    by_weekday_series = df.groupby(df["date"].dt.dayofweek)["waste_volume"].mean()
    by_weekday = [
        {
            "day": _DAY_LABELS[day_index],
            "average": round(float(by_weekday_series.get(day_index, 0.0)), 2),
        }
        for day_index in range(7)
    ]

    # Average volume per calendar month.
    monthly_series = (
        df.groupby(df["date"].dt.to_period("M"))["waste_volume"].mean().sort_index()
    )
    monthly = [
        {"month": str(period), "average": round(float(value), 2)}
        for period, value in monthly_series.items()
    ]

    # Correlation matrix across numeric drivers and the target.
    corr = df[_CORRELATION_COLUMNS].corr().round(3)
    correlation = {
        "columns": _CORRELATION_COLUMNS,
        "matrix": [[float(corr.iloc[i, j]) for j in range(len(_CORRELATION_COLUMNS))]
                   for i in range(len(_CORRELATION_COLUMNS))],
    }

    return {
        "distribution": distribution,
        "by_weekday": by_weekday,
        "monthly": monthly,
        "correlation": correlation,
        "sample_rows": _sample_rows(df),
    }


def _sample_rows(df: pd.DataFrame, limit: int = 20) -> List[Dict[str, Any]]:
    """First rows of the dataset for a preview table."""
    preview = df.head(limit).copy()
    preview["date"] = preview["date"].dt.strftime("%Y-%m-%d")
    return preview.to_dict(orient="records")
