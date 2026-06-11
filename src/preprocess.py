"""
Data preprocessing module for waste volume prediction
Handles data loading, feature engineering, and train-test splitting
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, List
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


REQUIRED_COLUMNS = [
    'date', 'temperature', 'rainfall', 'humidity', 
    'holiday', 'weekend', 'population_density', 
    'event_level', 'waste_volume'
]


def validate_dataset(df: pd.DataFrame) -> None:
    """
    Validate that dataset has all required columns
    
    Args:
        df: Input DataFrame
        
    Raises:
        ValueError: If required columns are missing
    """
    missing_cols = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    print(f"[OK] Dataset validation passed - all {len(REQUIRED_COLUMNS)} required columns present")


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values in dataset
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with missing values handled
    """
    missing_count = df.isnull().sum().sum()
    
    if missing_count > 0:
        print(f"Warning: Found {missing_count} missing values")
        
        # Fill numeric columns with median
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().any():
                median_val = df[col].median()
                df[col].fillna(median_val, inplace=True)
                print(f"  Filled {col} with median: {median_val:.2f}")
        
        # Fill categorical with mode
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if df[col].isnull().any():
                mode_val = df[col].mode()[0]
                df[col].fillna(mode_val, inplace=True)
                print(f"  Filled {col} with mode: {mode_val}")
    else:
        print("[OK] No missing values found")
    
    return df


def engineer_date_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract features from date column
    
    Args:
        df: Input DataFrame with 'date' column
        
    Returns:
        DataFrame with additional date features
    """
    print("Engineering date features...")
    
    # Convert date to datetime if it's not already
    if df['date'].dtype == 'object':
        df['date'] = pd.to_datetime(df['date'])
    
    # Extract date features
    df['day'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['day_of_week'] = df['date'].dt.dayofweek  # Monday=0, Sunday=6
    df['week_of_year'] = df['date'].dt.isocalendar().week.astype(int)
    df['is_month_start'] = df['date'].dt.is_month_start.astype(int)
    df['is_month_end'] = df['date'].dt.is_month_end.astype(int)
    
    print("[OK] Created 7 date features: day, month, year, day_of_week, week_of_year, is_month_start, is_month_end")
    
    return df


def prepare_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
    """
    Prepare features and target for model training
    
    Args:
        df: Input DataFrame
        
    Returns:
        Tuple of (X features, y target, feature_names)
    """
    print("\nPreparing features and target...")
    
    # Drop date column for training
    df_model = df.drop('date', axis=1)
    
    # Separate features and target
    X = df_model.drop('waste_volume', axis=1)
    y = df_model['waste_volume']
    
    feature_names = X.columns.tolist()
    
    print(f"[OK] Features shape: {X.shape}")
    print(f"[OK] Target shape: {y.shape}")
    print(f"[OK] Number of features: {len(feature_names)}")
    
    return X, y, feature_names


def split_data(
    X: pd.DataFrame, 
    y: pd.Series, 
    test_size: float = 0.2, 
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Split data into training and testing sets
    
    Args:
        X: Features DataFrame
        y: Target Series
        test_size: Proportion of test set (default 0.2)
        random_state: Random seed for reproducibility
        
    Returns:
        Tuple of (X_train, X_test, y_train, y_test)
    """
    print(f"\nSplitting data (train: {int((1-test_size)*100)}%, test: {int(test_size*100)}%)...")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    print(f"[OK] Training set: {X_train.shape[0]} samples")
    print(f"[OK] Test set: {X_test.shape[0]} samples")
    
    return X_train, X_test, y_train, y_test


def scale_features(
    X_train: pd.DataFrame, 
    X_test: pd.DataFrame,
    apply_scaling: bool = False
) -> Tuple[pd.DataFrame, pd.DataFrame, StandardScaler]:
    """
    Scale features using StandardScaler (optional)
    
    Args:
        X_train: Training features
        X_test: Test features
        apply_scaling: Whether to apply scaling
        
    Returns:
        Tuple of (X_train_scaled, X_test_scaled, scaler)
    """
    if not apply_scaling:
        print("\n[OK] Scaling not applied (tree-based models don't require scaling)")
        return X_train, X_test, None
    
    print("\nScaling features...")
    scaler = StandardScaler()
    
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train),
        columns=X_train.columns,
        index=X_train.index
    )
    
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test),
        columns=X_test.columns,
        index=X_test.index
    )
    
    print("[OK] Features scaled using StandardScaler")
    
    return X_train_scaled, X_test_scaled, scaler


def load_and_preprocess(
    data_path: str,
    test_size: float = 0.2,
    random_state: int = 42,
    apply_scaling: bool = False
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, List[str], StandardScaler]:
    """
    Complete preprocessing pipeline
    
    Args:
        data_path: Path to raw dataset CSV
        test_size: Proportion of test set
        random_state: Random seed
        apply_scaling: Whether to apply feature scaling
        
    Returns:
        Tuple of (X_train, X_test, y_train, y_test, feature_names, scaler)
    """
    print("="*60)
    print("STARTING DATA PREPROCESSING PIPELINE")
    print("="*60)
    
    # Load dataset
    print(f"\nLoading dataset from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"[OK] Loaded {len(df)} rows and {len(df.columns)} columns")
    
    # Validate dataset
    validate_dataset(df)
    
    # Handle missing values
    df = handle_missing_values(df)
    
    # Engineer date features
    df = engineer_date_features(df)
    
    # Prepare features and target
    X, y, feature_names = prepare_features(df)
    
    # Split data
    X_train, X_test, y_train, y_test = split_data(X, y, test_size, random_state)
    
    # Scale features (optional)
    X_train, X_test, scaler = scale_features(X_train, X_test, apply_scaling)
    
    print("\n" + "="*60)
    print("PREPROCESSING COMPLETED SUCCESSFULLY")
    print("="*60)
    
    return X_train, X_test, y_train, y_test, feature_names, scaler


if __name__ == "__main__":
    # Test preprocessing
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent
    data_path = project_root / "data" / "raw" / "waste_dataset.csv"
    
    if not data_path.exists():
        print(f"Dataset not found at {data_path}")
        print("Please run data_generator.py first to create the dataset")
    else:
        X_train, X_test, y_train, y_test, feature_names, scaler = load_and_preprocess(
            str(data_path)
        )
        
        print("\nFeature names:")
        for i, name in enumerate(feature_names, 1):
            print(f"  {i}. {name}")
        
        print("\nTarget statistics:")
        print(f"  Train mean: {y_train.mean():.2f} tons")
        print(f"  Train std: {y_train.std():.2f} tons")
        print(f"  Test mean: {y_test.mean():.2f} tons")
        print(f"  Test std: {y_test.std():.2f} tons")
