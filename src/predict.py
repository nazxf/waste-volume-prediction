"""
Prediction module for waste volume forecasting
Provides WasteVolumePredictor class for daily, weekly, and monthly predictions
"""
import pandas as pd
from pathlib import Path
from typing import Dict, Union, List
from datetime import datetime, timedelta
import joblib


class WasteVolumePredictor:
    """
    Waste Volume Predictor class for making predictions
    """
    
    def __init__(
        self,
        model_path: str = None,
        feature_columns_path: str = None,
        metadata_path: str = None,
        anomaly_detector_path: str = None
    ):
        """
        Initialize predictor with trained model
        
        Args:
            model_path: Path to saved model file
            feature_columns_path: Path to saved feature columns file
        """
        project_root = Path(__file__).parent.parent

        if model_path is None:
            model_path = project_root / "models" / "best_model.pkl"
        
        if feature_columns_path is None:
            feature_columns_path = project_root / "models" / "feature_columns.pkl"

        if metadata_path is None:
            metadata_path = project_root / "models" / "prediction_metadata.pkl"

        if anomaly_detector_path is None:
            anomaly_detector_path = project_root / "models" / "anomaly_detector.pkl"
        
        self.model_path = Path(model_path)
        self.feature_columns_path = Path(feature_columns_path)
        self.metadata_path = Path(metadata_path)
        self.anomaly_detector_path = Path(anomaly_detector_path)
        self.prediction_metadata = {}
        self.anomaly_detector = None
        
        # Load model and feature columns
        self._load_model()
        self._load_feature_columns()
        self._load_phase2_artifacts()
    
    def _load_model(self) -> None:
        """Load trained model from disk"""
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model file not found at {self.model_path}\n"
                "Please run 'python src/train_model.py' first to train the model."
            )
        
        self.model = joblib.load(self.model_path)
        print(f"[OK] Model loaded from {self.model_path}")
    
    def _load_feature_columns(self) -> None:
        """Load feature columns list from disk"""
        if not self.feature_columns_path.exists():
            raise FileNotFoundError(
                f"Feature columns file not found at {self.feature_columns_path}\n"
                "Please run 'python src/train_model.py' first to train the model."
            )
        
        self.feature_columns = joblib.load(self.feature_columns_path)
        print(f"[OK] Feature columns loaded: {len(self.feature_columns)} features")

    def _load_phase2_artifacts(self) -> None:
        """Load optional Phase 2 metadata and anomaly detector artifacts."""
        if self.metadata_path.exists():
            self.prediction_metadata = joblib.load(self.metadata_path)
            print(f"[OK] Prediction metadata loaded from {self.metadata_path}")

        if self.anomaly_detector_path.exists():
            self.anomaly_detector = joblib.load(self.anomaly_detector_path)
            print(f"[OK] Anomaly detector loaded from {self.anomaly_detector_path}")
    
    def _extract_date_features(self, date: Union[str, datetime]) -> Dict[str, int]:
        """
        Extract date features from a date
        
        Args:
            date: Date as string (YYYY-MM-DD) or datetime object
            
        Returns:
            Dictionary of date features
        """
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d")

        next_month = (date.replace(day=28) + timedelta(days=4)).replace(day=1)
        last_day = (next_month - timedelta(days=1)).day
        
        return {
            'day': date.day,
            'month': date.month,
            'year': date.year,
            'day_of_week': date.weekday(),
            'week_of_year': date.isocalendar()[1],
            'is_month_start': 1 if date.day == 1 else 0,
            'is_month_end': 1 if date.day == last_day else 0
        }

    def _is_known_holiday(self, date: datetime, fallback: int = 0) -> int:
        """
        Return a holiday flag for known Indonesian holidays.

        The predictor keeps the same simplified calendar logic as the
        synthetic data generator and preserves the user-provided flag for the
        requested start date.
        """
        if fallback:
            return 1

        fixed_holidays = {
            (1, 1),
            (5, 1),
            (6, 1),
            (8, 17),
            (12, 25),
        }

        eid_dates = {
            2020: {(5, 24), (5, 25)},
            2021: {(5, 13), (5, 14)},
            2022: {(5, 2), (5, 3)},
            2023: {(4, 22), (4, 23)},
            2024: {(4, 10), (4, 11)},
        }

        if (date.month, date.day) in fixed_holidays:
            return 1

        return int((date.month, date.day) in eid_dates.get(date.year, set()))
    
    def _prepare_input(self, input_data: Dict) -> pd.DataFrame:
        """
        Prepare input data for prediction
        
        Args:
            input_data: Dictionary with input features
            
        Returns:
            DataFrame ready for prediction
        """
        # Extract date features
        date_features = self._extract_date_features(input_data['date'])
        
        # Combine all features
        features = {
            'temperature': input_data['temperature'],
            'rainfall': input_data['rainfall'],
            'humidity': input_data['humidity'],
            'holiday': input_data['holiday'],
            'weekend': input_data['weekend'],
            'population_density': input_data['population_density'],
            'event_level': input_data['event_level'],
            **date_features
        }
        
        # Create DataFrame with correct column order
        df = pd.DataFrame([features])
        df = df[self.feature_columns]
        
        return df
    
    def predict_daily(self, input_data: Dict) -> float:
        """
        Predict waste volume for a single day
        
        Args:
            input_data: Dictionary with keys:
                - date: Date string (YYYY-MM-DD)
                - temperature: Temperature in Celsius
                - rainfall: Rainfall in mm
                - humidity: Humidity percentage
                - holiday: 0 or 1
                - weekend: 0 or 1
                - population_density: Population density (people/km2)
                - event_level: Event level (0-5)
        
        Returns:
            Predicted waste volume in tons
        """
        X = self._prepare_input(input_data)
        prediction = self.model.predict(X)[0]
        return float(prediction)

    def calculate_confidence_interval(
        self,
        prediction: float,
        confidence: float = 0.95,
        horizon_days: int = 1
    ) -> Dict[str, float]:
        """
        Calculate a residual-based confidence interval for a prediction.

        Args:
            prediction: Predicted waste volume
            confidence: Confidence level, for example 0.80, 0.90, or 0.95
            horizon_days: Number of independent days represented by prediction

        Returns:
            Dictionary with lower/upper bounds and margin of error
        """
        margins = self.prediction_metadata.get('interval_margins', {})
        margin = margins.get(f"{confidence:.2f}")

        if margin is None:
            residual_std = self.prediction_metadata.get('residual_std', 0.0)
            z_scores = {0.80: 1.282, 0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
            z_score = z_scores.get(round(confidence, 2), 1.96)
            margin = z_score * residual_std

        adjusted_margin = float(margin) * (max(1, horizon_days) ** 0.5)
        lower_bound = max(0.0, prediction - adjusted_margin)
        upper_bound = prediction + adjusted_margin

        return {
            'confidence': confidence,
            'lower_bound': round(lower_bound, 2),
            'upper_bound': round(upper_bound, 2),
            'margin_of_error': round(adjusted_margin, 2)
        }

    def detect_anomaly(self, input_data: Dict) -> Dict[str, Union[bool, float, str]]:
        """
        Detect whether an input looks unusual compared with training data.

        Args:
            input_data: Prediction input dictionary

        Returns:
            Dictionary with anomaly flag and score
        """
        if self.anomaly_detector is None:
            return {
                'is_anomaly': False,
                'score': None,
                'message': 'Anomaly detector is not available. Run training first.'
            }

        X = self._prepare_input(input_data)
        label = int(self.anomaly_detector.predict(X)[0])
        score = float(self.anomaly_detector.decision_function(X)[0])

        return {
            'is_anomaly': label == -1,
            'score': round(score, 4),
            'message': 'Input is outside normal training patterns' if label == -1 else 'Input is within normal training patterns'
        }

    def predict_daily_with_details(self, input_data: Dict, confidence: float = 0.95) -> Dict:
        """
        Predict one day with confidence interval, anomaly status, and fleet plan.
        """
        prediction = self.predict_daily(input_data)
        return {
            'date': input_data['date'],
            'predicted_waste_volume': round(prediction, 2),
            'unit': 'tons',
            'confidence_interval': self.calculate_confidence_interval(prediction, confidence),
            'anomaly': self.detect_anomaly(input_data),
            'fleet_recommendation': self.calculate_fleet_recommendation(prediction)
        }
    
    def predict_weekly(self, input_data: Dict) -> Dict[str, Union[float, List[Dict]]]:
        """
        Predict total waste volume for 7 consecutive days
        
        Args:
            input_data: Dictionary with base input features
        
        Returns:
            Dictionary with total_volume and daily_predictions list
        """
        # Parse start date
        start_date = datetime.strptime(input_data['date'], "%Y-%m-%d")
        
        daily_predictions = []
        total_volume = 0.0
        
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            
            # Update input for current day
            day_input = input_data.copy()
            day_input['date'] = current_date.strftime("%Y-%m-%d")
            
            # Update weekend flag
            day_input['weekend'] = 1 if current_date.weekday() >= 5 else 0
            day_input['holiday'] = self._is_known_holiday(
                current_date,
                fallback=input_data.get('holiday', 0) if i == 0 else 0
            )
            
            # Predict for this day
            details = self.predict_daily_with_details(day_input)
            prediction = details['predicted_waste_volume']
            total_volume += prediction
            
            daily_predictions.append({
                'date': day_input['date'],
                'day_name': current_date.strftime("%A"),
                'predicted_volume': round(prediction, 2),
                'confidence_interval': details['confidence_interval'],
                'anomaly': details['anomaly']
            })
        
        return {
            'total_volume': round(total_volume, 2),
            'average_daily': round(total_volume / 7, 2),
            'confidence_interval': self.calculate_confidence_interval(total_volume, horizon_days=7),
            'daily_predictions': daily_predictions
        }
    
    def predict_monthly(self, input_data: Dict) -> Dict[str, Union[float, List[Dict]]]:
        """
        Predict total waste volume for 30 consecutive days
        
        Args:
            input_data: Dictionary with base input features
        
        Returns:
            Dictionary with total_volume and daily_predictions list
        """
        # Parse start date
        start_date = datetime.strptime(input_data['date'], "%Y-%m-%d")
        
        daily_predictions = []
        total_volume = 0.0
        
        for i in range(30):
            current_date = start_date + timedelta(days=i)
            
            # Update input for current day
            day_input = input_data.copy()
            day_input['date'] = current_date.strftime("%Y-%m-%d")
            
            # Update weekend flag
            day_input['weekend'] = 1 if current_date.weekday() >= 5 else 0
            day_input['holiday'] = self._is_known_holiday(
                current_date,
                fallback=input_data.get('holiday', 0) if i == 0 else 0
            )
            
            # Predict for this day
            details = self.predict_daily_with_details(day_input)
            prediction = details['predicted_waste_volume']
            total_volume += prediction
            
            daily_predictions.append({
                'date': day_input['date'],
                'day_name': current_date.strftime("%A"),
                'predicted_volume': round(prediction, 2),
                'confidence_interval': details['confidence_interval'],
                'anomaly': details['anomaly']
            })
        
        return {
            'total_volume': round(total_volume, 2),
            'average_daily': round(total_volume / 30, 2),
            'confidence_interval': self.calculate_confidence_interval(total_volume, horizon_days=30),
            'daily_predictions': daily_predictions
        }
    
    def calculate_fleet_recommendation(self, predicted_volume: float, truck_capacity: float = 8.0) -> Dict[str, Union[int, float]]:
        """
        Calculate recommended number of trucks for waste collection
        
        Args:
            predicted_volume: Predicted waste volume in tons
            truck_capacity: Capacity of one truck in tons (default 8.0)
        
        Returns:
            Dictionary with fleet recommendations
        """
        import math
        
        if truck_capacity <= 0:
            raise ValueError("Truck capacity must be greater than zero")

        predicted_volume = max(0.0, predicted_volume)
        trucks_needed = max(1, math.ceil(predicted_volume / truck_capacity))
        
        return {
            'trucks_needed': trucks_needed,
            'truck_capacity': truck_capacity,
            'total_capacity': trucks_needed * truck_capacity,
            'utilization_rate': round((predicted_volume / (trucks_needed * truck_capacity)) * 100, 2)
        }


def example_prediction():
    """Example usage of WasteVolumePredictor"""
    try:
        predictor = WasteVolumePredictor()
        
        # Example input
        input_data = {
            'date': '2025-01-15',
            'temperature': 30.5,
            'rainfall': 5.0,
            'humidity': 75.0,
            'holiday': 0,
            'weekend': 0,
            'population_density': 9500,
            'event_level': 1
        }
        
        print("\n" + "="*60)
        print("WASTE VOLUME PREDICTION EXAMPLE")
        print("="*60)
        
        # Daily prediction
        print("\n1. DAILY PREDICTION")
        print("-" * 60)
        daily_pred = predictor.predict_daily(input_data)
        print(f"Date: {input_data['date']}")
        print(f"Predicted waste volume: {daily_pred:.2f} tons")
        
        fleet = predictor.calculate_fleet_recommendation(daily_pred)
        print(f"Recommended trucks: {fleet['trucks_needed']} trucks")
        print(f"Fleet utilization: {fleet['utilization_rate']}%")
        
        # Weekly prediction
        print("\n2. WEEKLY PREDICTION (7 days)")
        print("-" * 60)
        weekly_pred = predictor.predict_weekly(input_data)
        print(f"Total weekly volume: {weekly_pred['total_volume']:.2f} tons")
        print(f"Average daily volume: {weekly_pred['average_daily']:.2f} tons")
        print("\nDaily breakdown:")
        for day in weekly_pred['daily_predictions'][:3]:
            print(f"  {day['date']} ({day['day_name']}): {day['predicted_volume']:.2f} tons")
        print(f"  ... and {len(weekly_pred['daily_predictions']) - 3} more days")
        
        # Monthly prediction
        print("\n3. MONTHLY PREDICTION (30 days)")
        print("-" * 60)
        monthly_pred = predictor.predict_monthly(input_data)
        print(f"Total monthly volume: {monthly_pred['total_volume']:.2f} tons")
        print(f"Average daily volume: {monthly_pred['average_daily']:.2f} tons")
        
        fleet = predictor.calculate_fleet_recommendation(monthly_pred['average_daily'])
        print(f"Recommended daily fleet: {fleet['trucks_needed']} trucks")
        
        print("\n" + "="*60)
        
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        print("\nPlease train the model first by running:")
        print("  python src/train_model.py")


if __name__ == "__main__":
    example_prediction()
