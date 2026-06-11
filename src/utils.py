"""
Utility functions for the Waste Volume Prediction System
"""
import logging
from pathlib import Path
from typing import Union
import joblib

# Setup logging
def setup_logging(log_file: str = None) -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        log_file: Optional log file path
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_project_root() -> Path:
    """
    Get the project root directory
    
    Returns:
        Path object pointing to project root
    """
    return Path(__file__).parent.parent


def ensure_dir(directory: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        directory: Directory path
        
    Returns:
        Path object
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def save_model(model, filepath: Union[str, Path]) -> None:
    """
    Save model to disk using joblib
    
    Args:
        model: Model object to save
        filepath: Path to save the model
    """
    filepath = Path(filepath)
    ensure_dir(filepath.parent)
    joblib.dump(model, filepath)
    print(f"Model saved to {filepath}")


def load_model(filepath: Union[str, Path]):
    """
    Load model from disk using joblib
    
    Args:
        filepath: Path to the saved model
        
    Returns:
        Loaded model object
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Model file not found: {filepath}")
    return joblib.load(filepath)


def format_number(number: float, decimals: int = 2) -> str:
    """
    Format number with specified decimal places
    
    Args:
        number: Number to format
        decimals: Number of decimal places
        
    Returns:
        Formatted string
    """
    return f"{number:.{decimals}f}"


logger = setup_logging()
