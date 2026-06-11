"""
Model training script for waste volume prediction
Trains Random Forest and XGBoost models, compares them, and saves the best one
"""
import sys
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Add src to path
sys.path.append(str(Path(__file__).parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from xgboost import XGBRegressor
import joblib

from data_generator import generate_waste_dataset
from ensemble import WasteEnsembleRegressor
from preprocess import load_and_preprocess
from evaluate import (
    calculate_metrics, 
    compare_models, 
    print_metrics,
    create_evaluation_report
)
from utils import save_model, ensure_dir, logger


def check_and_generate_dataset(data_path: Path) -> None:
    """
    Check if dataset exists, generate if not
    
    Args:
        data_path: Path to dataset file
    """
    if not data_path.exists():
        logger.info(f"Dataset not found at {data_path}")
        logger.info("Generating synthetic dataset...")
        generate_waste_dataset(output_path=str(data_path))
        logger.info("Dataset generated successfully!")
    else:
        logger.info(f"Dataset found at {data_path}")


def train_random_forest(X_train, y_train, X_test, y_test):
    """
    Train Random Forest Regressor
    
    Args:
        X_train: Training features
        y_train: Training target
        X_test: Test features
        y_test: Test target
    
    Returns:
        Tuple of (model, train_metrics, test_metrics, feature_importance)
    """
    print("\n" + "="*60)
    print("TRAINING RANDOM FOREST REGRESSOR")
    print("="*60)
    
    # Initialize model with specified parameters
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        random_state=42,
        n_jobs=-1,
        verbose=0
    )
    
    print("\nModel parameters:")
    print(f"  n_estimators: 200")
    print(f"  max_depth: 12")
    print(f"  random_state: 42")
    print(f"  n_jobs: -1 (use all CPU cores)")
    
    # Train model
    print("\nTraining model...")
    model.fit(X_train, y_train)
    print("[OK] Training completed!")
    
    # Predictions
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    # Calculate metrics
    train_metrics = calculate_metrics(y_train, y_train_pred)
    test_metrics = calculate_metrics(y_test, y_test_pred)
    
    print_metrics(train_metrics, "Random Forest - Training Set")
    print_metrics(test_metrics, "Random Forest - Test Set")
    
    # Feature importance
    feature_importance = dict(zip(X_train.columns, model.feature_importances_))
    
    return model, train_metrics, test_metrics, feature_importance


def train_xgboost(X_train, y_train, X_test, y_test):
    """
    Train XGBoost Regressor
    
    Args:
        X_train: Training features
        y_train: Training target
        X_test: Test features
        y_test: Test target
    
    Returns:
        Tuple of (model, train_metrics, test_metrics, feature_importance)
    """
    print("\n" + "="*60)
    print("TRAINING XGBOOST REGRESSOR")
    print("="*60)
    
    # Initialize model with specified parameters
    model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        objective='reg:squarederror',
        n_jobs=-1,
        verbosity=0
    )
    
    print("\nModel parameters:")
    print(f"  n_estimators: 300")
    print(f"  learning_rate: 0.05")
    print(f"  max_depth: 6")
    print(f"  subsample: 0.8")
    print(f"  colsample_bytree: 0.8")
    print(f"  random_state: 42")
    print(f"  objective: reg:squarederror")
    
    # Train model
    print("\nTraining model...")
    model.fit(X_train, y_train)
    print("[OK] Training completed!")
    
    # Predictions
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    # Calculate metrics
    train_metrics = calculate_metrics(y_train, y_train_pred)
    test_metrics = calculate_metrics(y_test, y_test_pred)
    
    print_metrics(train_metrics, "XGBoost - Training Set")
    print_metrics(test_metrics, "XGBoost - Test Set")
    
    # Feature importance
    feature_importance = dict(zip(X_train.columns, model.feature_importances_))
    
    return model, train_metrics, test_metrics, feature_importance


def train_voting_ensemble(rf_model, xgb_model, X_train, y_train, X_test, y_test):
    """
    Create and evaluate a voting ensemble from fitted base models.

    Args:
        rf_model: Fitted Random Forest model
        xgb_model: Fitted XGBoost model
        X_train: Training features
        y_train: Training target
        X_test: Test features
        y_test: Test target

    Returns:
        Tuple of (model, train_metrics, test_metrics, feature_importance)
    """
    print("\n" + "="*60)
    print("TRAINING VOTING ENSEMBLE")
    print("="*60)

    model = WasteEnsembleRegressor({
        'Random Forest': rf_model,
        'XGBoost': xgb_model,
    })

    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    train_metrics = calculate_metrics(y_train, y_train_pred)
    test_metrics = calculate_metrics(y_test, y_test_pred)

    print_metrics(train_metrics, "Voting Ensemble - Training Set")
    print_metrics(test_metrics, "Voting Ensemble - Test Set")

    rf_importance = dict(zip(X_train.columns, rf_model.feature_importances_))
    xgb_importance = dict(zip(X_train.columns, xgb_model.feature_importances_))
    feature_importance = {
        feature: float((rf_importance[feature] + xgb_importance[feature]) / 2)
        for feature in X_train.columns
    }

    return model, train_metrics, test_metrics, feature_importance


def train_anomaly_detector(X_train):
    """
    Train an Isolation Forest anomaly detector for input feature outliers.

    Args:
        X_train: Training features

    Returns:
        Tuple of (detector, summary)
    """
    print("\n" + "="*60)
    print("TRAINING ANOMALY DETECTOR")
    print("="*60)

    detector = IsolationForest(
        n_estimators=200,
        contamination=0.03,
        random_state=42,
        n_jobs=-1
    )
    detector.fit(X_train)

    labels = detector.predict(X_train)
    anomaly_count = int((labels == -1).sum())
    summary = {
        'algorithm': 'IsolationForest',
        'contamination': 0.03,
        'training_samples': int(X_train.shape[0]),
        'training_anomalies': anomaly_count,
        'training_anomaly_rate': round(anomaly_count / X_train.shape[0], 4)
    }

    print(f"[OK] Anomaly detector trained on {summary['training_samples']} samples")
    print(f"[OK] Training anomalies detected: {summary['training_anomalies']} ({summary['training_anomaly_rate']*100:.2f}%)")

    return detector, summary


def create_prediction_metadata(best_model, best_model_name, best_metrics, X_test, y_test, anomaly_summary):
    """
    Create metadata used for prediction intervals and model introspection.

    Args:
        best_model: Selected best model
        best_model_name: Selected model name
        best_metrics: Test-set metrics for the best model
        X_test: Test features
        y_test: Test target
        anomaly_summary: Summary from anomaly detector training

    Returns:
        Metadata dictionary
    """
    y_pred = best_model.predict(X_test)
    residuals = np.asarray(y_test) - np.asarray(y_pred)
    abs_residuals = np.abs(residuals)

    interval_margins = {
        '0.80': float(np.quantile(abs_residuals, 0.80)),
        '0.90': float(np.quantile(abs_residuals, 0.90)),
        '0.95': float(np.quantile(abs_residuals, 0.95)),
    }

    return {
        'best_model_name': best_model_name,
        'trained_at': datetime.utcnow().isoformat(timespec='seconds') + 'Z',
        'test_metrics': {key: float(value) for key, value in best_metrics.items()},
        'residual_std': float(np.std(residuals)),
        'interval_margins': interval_margins,
        'anomaly_detector': anomaly_summary,
    }


def plot_feature_importance(feature_importance: dict, output_path: Path, top_n: int = 15):
    """
    Plot and save feature importance chart
    
    Args:
        feature_importance: Dictionary of feature importances
        output_path: Path to save the plot
        top_n: Number of top features to display
    """
    print(f"\nCreating feature importance plot (top {top_n} features)...")
    
    # Sort features by importance
    sorted_features = sorted(
        feature_importance.items(),
        key=lambda x: x[1],
        reverse=True
    )[:top_n]
    
    features, importances = zip(*sorted_features)
    
    # Create plot
    plt.figure(figsize=(10, 8))
    plt.barh(range(len(features)), importances, color='steelblue')
    plt.yticks(range(len(features)), features)
    plt.xlabel('Importance Score', fontsize=12, fontweight='bold')
    plt.ylabel('Features', fontsize=12, fontweight='bold')
    plt.title(f'Top {top_n} Feature Importances', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    
    # Save plot
    ensure_dir(output_path.parent)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"[OK] Feature importance plot saved to {output_path}")
    plt.close()


def plot_prediction_comparison(y_test, y_pred_rf, y_pred_xgb, output_path: Path):
    """
    Plot actual vs predicted values comparison
    
    Args:
        y_test: Actual values
        y_pred_rf: Random Forest predictions
        y_pred_xgb: XGBoost predictions
        output_path: Path to save the plot
    """
    print("\nCreating prediction comparison plot...")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Random Forest
    axes[0].scatter(y_test, y_pred_rf, alpha=0.5, color='steelblue')
    axes[0].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 
                 'r--', lw=2, label='Perfect Prediction')
    axes[0].set_xlabel('Actual Waste Volume (tons)', fontsize=11)
    axes[0].set_ylabel('Predicted Waste Volume (tons)', fontsize=11)
    axes[0].set_title('Random Forest: Actual vs Predicted', fontsize=12, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # XGBoost
    axes[1].scatter(y_test, y_pred_xgb, alpha=0.5, color='darkgreen')
    axes[1].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 
                 'r--', lw=2, label='Perfect Prediction')
    axes[1].set_xlabel('Actual Waste Volume (tons)', fontsize=11)
    axes[1].set_ylabel('Predicted Waste Volume (tons)', fontsize=11)
    axes[1].set_title('XGBoost: Actual vs Predicted', fontsize=12, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"[OK] Prediction comparison plot saved to {output_path}")
    plt.close()


def main():
    """Main training pipeline"""
    print("\n" + "="*60)
    print("WASTE VOLUME PREDICTION - MODEL TRAINING")
    print("="*60)
    
    # Setup paths
    project_root = Path(__file__).parent.parent
    data_path = project_root / "data" / "raw" / "waste_dataset.csv"
    models_dir = project_root / "models"
    reports_dir = project_root / "reports"
    
    # Ensure directories exist
    ensure_dir(models_dir)
    ensure_dir(reports_dir)
    
    # Step 1: Check and generate dataset
    check_and_generate_dataset(data_path)
    
    # Step 2: Load and preprocess data
    print("\n" + "="*60)
    print("STEP 1: DATA PREPROCESSING")
    print("="*60)
    
    X_train, X_test, y_train, y_test, feature_names, scaler = load_and_preprocess(
        str(data_path),
        test_size=0.2,
        random_state=42,
        apply_scaling=False  # Tree-based models don't need scaling
    )
    
    # Step 3: Train Random Forest
    print("\n" + "="*60)
    print("STEP 2: MODEL TRAINING")
    print("="*60)
    
    rf_model, rf_train_metrics, rf_test_metrics, rf_importance = train_random_forest(
        X_train, y_train, X_test, y_test
    )
    
    # Step 4: Train XGBoost
    xgb_model, xgb_train_metrics, xgb_test_metrics, xgb_importance = train_xgboost(
        X_train, y_train, X_test, y_test
    )

    # Step 5: Create voting ensemble
    ensemble_model, ensemble_train_metrics, ensemble_test_metrics, ensemble_importance = train_voting_ensemble(
        rf_model, xgb_model, X_train, y_train, X_test, y_test
    )

    # Step 6: Train anomaly detector
    anomaly_detector, anomaly_summary = train_anomaly_detector(X_train)
    
    # Step 7: Compare models
    print("\n" + "="*60)
    print("STEP 3: MODEL COMPARISON")
    print("="*60)
    
    test_results = {
        'Random Forest': rf_test_metrics,
        'XGBoost': xgb_test_metrics,
        'Ensemble': ensemble_test_metrics
    }
    
    best_model_name, best_metrics = compare_models(test_results)
    
    # Select best model
    model_registry = {
        'Random Forest': (rf_model, rf_importance),
        'XGBoost': (xgb_model, xgb_importance),
        'Ensemble': (ensemble_model, ensemble_importance),
    }
    best_model, best_importance = model_registry[best_model_name]
    
    # Step 8: Save models
    print("\n" + "="*60)
    print("STEP 4: SAVING MODELS")
    print("="*60)
    
    save_model(rf_model, models_dir / "random_forest.pkl")
    save_model(xgb_model, models_dir / "xgboost.pkl")
    save_model(ensemble_model, models_dir / "ensemble_model.pkl")
    save_model(best_model, models_dir / "best_model.pkl")
    save_model(anomaly_detector, models_dir / "anomaly_detector.pkl")
    
    # Save feature columns for prediction
    joblib.dump(feature_names, models_dir / "feature_columns.pkl")
    print(f"[OK] Feature columns saved to {models_dir / 'feature_columns.pkl'}")

    prediction_metadata = create_prediction_metadata(
        best_model=best_model,
        best_model_name=best_model_name,
        best_metrics=best_metrics,
        X_test=X_test,
        y_test=y_test,
        anomaly_summary=anomaly_summary
    )
    joblib.dump(prediction_metadata, models_dir / "prediction_metadata.pkl")
    print(f"[OK] Prediction metadata saved to {models_dir / 'prediction_metadata.pkl'}")
    
    # Step 9: Generate evaluation report
    print("\n" + "="*60)
    print("STEP 5: GENERATING REPORTS")
    print("="*60)
    
    report_path = reports_dir / "evaluation_report.md"
    create_evaluation_report(
        results=test_results,
        best_model_name=best_model_name,
        feature_importance=best_importance,
        output_path=str(report_path)
    )
    
    # Step 8: Create visualizations
    plot_feature_importance(
        best_importance,
        reports_dir / "feature_importance.png",
        top_n=15
    )
    
    # Get predictions for comparison plot
    y_pred_rf = rf_model.predict(X_test)
    y_pred_xgb = xgb_model.predict(X_test)
    
    plot_prediction_comparison(
        y_test,
        y_pred_rf,
        y_pred_xgb,
        reports_dir / "prediction_comparison.png"
    )
    
    # Final summary
    print("\n" + "="*60)
    print("TRAINING COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"\nBest Model: {best_model_name}")
    print(f"   RMSE: {best_metrics['RMSE']:.4f} tons")
    print(f"   R2: {best_metrics['R2']:.4f}")
    print(f"   MAPE: {best_metrics['MAPE']:.2f}%")
    print(f"\nModels saved to: {models_dir}")
    print(f"Reports saved to: {reports_dir}")
    print(f"\nYou can now run the dashboard:")
    print(f"   streamlit run dashboard/app.py")
    print(f"\nOr start the API server:")
    print(f"   uvicorn api.main:app --reload")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
