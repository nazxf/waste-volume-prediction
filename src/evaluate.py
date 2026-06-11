"""
Model evaluation module for waste volume prediction
Contains metrics calculation and model comparison functions
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Calculate regression metrics
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        Dictionary with MAE, RMSE, R2, and MAPE
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    # Calculate MAPE (Mean Absolute Percentage Error)
    # Avoid division by zero
    mask = y_true != 0
    mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    
    return {
        'MAE': mae,
        'RMSE': rmse,
        'R2': r2,
        'MAPE': mape
    }


def print_metrics(metrics: Dict[str, float], model_name: str = "Model") -> None:
    """
    Print metrics in a formatted way
    
    Args:
        metrics: Dictionary of metrics
        model_name: Name of the model
    """
    print(f"\n{model_name} Performance Metrics:")
    print("-" * 50)
    print(f"  MAE (Mean Absolute Error):  {metrics['MAE']:.4f} tons")
    print(f"  RMSE (Root Mean Squared):   {metrics['RMSE']:.4f} tons")
    print(f"  R2 Score:                   {metrics['R2']:.4f}")
    print(f"  MAPE (Mean Abs % Error):    {metrics['MAPE']:.2f}%")
    print("-" * 50)


def compare_models(results: Dict[str, Dict[str, float]]) -> Tuple[str, Dict[str, float]]:
    """
    Compare multiple models and select the best one
    
    Args:
        results: Dictionary with model names as keys and metrics as values
        
    Returns:
        Tuple of (best_model_name, best_model_metrics)
    """
    print("\n" + "="*60)
    print("MODEL COMPARISON")
    print("="*60)
    
    # Create comparison DataFrame
    df = pd.DataFrame(results).T
    df = df.round(4)
    
    print("\nAll Models Performance:")
    print(df.to_string())
    
    # Find best model based on RMSE (lower is better)
    best_model = df['RMSE'].idxmin()
    best_metrics = results[best_model]
    
    print(f"\n{'='*60}")
    print(f"BEST MODEL: {best_model}")
    print(f"{'='*60}")
    print(f"  RMSE: {best_metrics['RMSE']:.4f} tons")
    print(f"  MAE:  {best_metrics['MAE']:.4f} tons")
    print(f"  R2:   {best_metrics['R2']:.4f}")
    print(f"  MAPE: {best_metrics['MAPE']:.2f}%")
    print("="*60)
    
    return best_model, best_metrics


def evaluate_model_predictions(
    y_true: np.ndarray, 
    y_pred: np.ndarray,
    model_name: str = "Model"
) -> Dict[str, float]:
    """
    Evaluate model predictions with detailed output
    
    Args:
        y_true: True values
        y_pred: Predicted values
        model_name: Name of the model
        
    Returns:
        Dictionary of metrics
    """
    metrics = calculate_metrics(y_true, y_pred)
    print_metrics(metrics, model_name)
    
    return metrics


def calculate_prediction_intervals(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    confidence: float = 0.95
) -> Dict[str, float]:
    """
    Calculate prediction intervals
    
    Args:
        y_true: True values
        y_pred: Predicted values
        confidence: Confidence level (default 0.95)
        
    Returns:
        Dictionary with interval statistics
    """
    residuals = y_true - y_pred
    std_residuals = np.std(residuals)
    
    # Calculate confidence interval
    z_score = 1.96 if confidence == 0.95 else 2.576  # 95% or 99%
    margin = z_score * std_residuals
    
    return {
        'std_residuals': std_residuals,
        'margin_of_error': margin,
        'lower_bound': -margin,
        'upper_bound': margin
    }


def create_evaluation_report(
    results: Dict[str, Dict[str, float]],
    best_model_name: str,
    feature_importance: Dict[str, float] = None,
    output_path: str = None
) -> str:
    """
    Create detailed evaluation report in Markdown format
    
    Args:
        results: Dictionary with model results
        best_model_name: Name of the best model
        feature_importance: Optional feature importance dictionary
        output_path: Path to save the report
        
    Returns:
        Markdown report string
    """
    report = []
    report.append("# Model Evaluation Report")
    report.append("\n## Executive Summary\n")
    report.append(f"**Best Model**: {best_model_name}\n")
    report.append(f"**Number of Models Evaluated**: {len(results)}\n")
    
    # Best model metrics
    best_metrics = results[best_model_name]
    report.append("\n## Best Model Performance\n")
    report.append("| Metric | Value |")
    report.append("|--------|-------|")
    report.append(f"| MAE (Mean Absolute Error) | {best_metrics['MAE']:.4f} tons |")
    report.append(f"| RMSE (Root Mean Squared Error) | {best_metrics['RMSE']:.4f} tons |")
    report.append(f"| R2 Score | {best_metrics['R2']:.4f} |")
    report.append(f"| MAPE (Mean Absolute Percentage Error) | {best_metrics['MAPE']:.2f}% |")
    
    # Model comparison
    report.append("\n## Model Comparison\n")
    report.append("| Model | MAE | RMSE | R2 | MAPE |")
    report.append("|-------|-----|------|-------|------|")
    
    for model_name, metrics in results.items():
        marker = " *" if model_name == best_model_name else ""
        report.append(
            f"| {model_name}{marker} | "
            f"{metrics['MAE']:.4f} | "
            f"{metrics['RMSE']:.4f} | "
            f"{metrics['R2']:.4f} | "
            f"{metrics['MAPE']:.2f}% |"
        )
    
    # Feature importance
    if feature_importance:
        report.append("\n## Feature Importance\n")
        report.append("| Rank | Feature | Importance |")
        report.append("|------|---------|------------|")
        
        sorted_features = sorted(
            feature_importance.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        for rank, (feature, importance) in enumerate(sorted_features[:10], 1):
            report.append(f"| {rank} | {feature} | {importance:.4f} |")
    
    # Interpretation
    report.append("\n## Interpretation\n")
    
    r2 = best_metrics['R2']
    if r2 >= 0.9:
        r2_interpretation = "Excellent"
    elif r2 >= 0.8:
        r2_interpretation = "Very Good"
    elif r2 >= 0.7:
        r2_interpretation = "Good"
    elif r2 >= 0.6:
        r2_interpretation = "Moderate"
    else:
        r2_interpretation = "Needs Improvement"
    
    report.append(f"- **R2 Score ({r2:.4f})**: {r2_interpretation} - The model explains {r2*100:.2f}% of the variance in waste volume.")
    report.append(f"- **RMSE ({best_metrics['RMSE']:.4f} tons)**: On average, predictions deviate by {best_metrics['RMSE']:.2f} tons from actual values.")
    report.append(f"- **MAPE ({best_metrics['MAPE']:.2f}%)**: Average prediction error is {best_metrics['MAPE']:.2f}% of actual values.")
    
    # Recommendations
    report.append("\n## Recommendations\n")
    report.append("1. **Deployment**: The model is ready for deployment in production environment.")
    report.append("2. **Monitoring**: Continuously monitor model performance with real-world data.")
    report.append("3. **Retraining**: Retrain the model quarterly with new data to maintain accuracy.")
    report.append("4. **Feature Engineering**: Consider adding more features like economic indicators or special events.")
    
    report_text = "\n".join(report)
    
    # Save to file if path provided
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"\n[OK] Evaluation report saved to {output_path}")
    
    return report_text


if __name__ == "__main__":
    # Test evaluation functions
    print("Testing evaluation module...")
    
    # Generate sample data
    np.random.seed(42)
    y_true = np.random.uniform(50, 150, 100)
    y_pred = y_true + np.random.normal(0, 5, 100)
    
    # Calculate metrics
    metrics = evaluate_model_predictions(y_true, y_pred, "Test Model")
    
    # Test comparison
    results = {
        'Random Forest': {'MAE': 3.45, 'RMSE': 4.23, 'R2': 0.91, 'MAPE': 4.5},
        'XGBoost': {'MAE': 3.12, 'RMSE': 3.98, 'R2': 0.93, 'MAPE': 4.2}
    }
    
    best_model, best_metrics = compare_models(results)
