"""
Lightweight ensemble model helpers for waste volume prediction.
"""
from typing import Dict, Iterable, Optional

import numpy as np


class WasteEnsembleRegressor:
    """
    Voting ensemble that averages predictions from fitted regressors.
    """

    def __init__(self, models: Dict[str, object], weights: Optional[Iterable[float]] = None):
        if not models:
            raise ValueError("At least one fitted model is required for the ensemble.")

        self.models = models
        self.model_names = list(models.keys())
        self.weights = None if weights is None else np.asarray(list(weights), dtype=float)

        if self.weights is not None and len(self.weights) != len(self.models):
            raise ValueError("Number of ensemble weights must match number of models.")

    def predict(self, X):
        """Predict by averaging fitted base-model predictions."""
        predictions = np.column_stack([
            model.predict(X) for model in self.models.values()
        ])

        if self.weights is None:
            return predictions.mean(axis=1)

        return np.average(predictions, axis=1, weights=self.weights)


