"""
Data generator for creating synthetic waste volume dataset
Generates 5 years of daily data from 2020-01-01 to 2024-12-31
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import List


def generate_dates(start_date: str, end_date: str) -> List[datetime]:
    """
    Generate list of dates between start and end date
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        List of datetime objects
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += timedelta(days=1)
    
    return dates


def is_indonesian_holiday(date: datetime) -> int:
    """
    Check if date is Indonesian holiday
    Simplified version with major holidays
    
    Args:
        date: Date to check
        
    Returns:
        1 if holiday, 0 otherwise
    """
    # Major Indonesian holidays (simplified)
    holidays = {
        (1, 1),   # New Year
        (5, 1),   # Labor Day
        (6, 1),   # Pancasila Day
        (8, 17),  # Independence Day
        (12, 25), # Christmas
    }
    
    # Eid al-Fitr (approximate, 2 days)
    eid_dates = {
        2020: [(5, 24), (5, 25)],
        2021: [(5, 13), (5, 14)],
        2022: [(5, 2), (5, 3)],
        2023: [(4, 22), (4, 23)],
        2024: [(4, 10), (4, 11)],
    }
    
    if (date.month, date.day) in holidays:
        return 1
    
    if date.year in eid_dates:
        if (date.month, date.day) in eid_dates[date.year]:
            return 1
    
    return 0


def generate_waste_dataset(
    start_date: str = "2020-01-01",
    end_date: str = "2024-12-31",
    output_path: str = None,
    random_state: int = 42
) -> pd.DataFrame:
    """
    Generate synthetic waste volume dataset with realistic patterns
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        output_path: Path to save the dataset (optional)
        random_state: Random seed for reproducible synthetic data
        
    Returns:
        DataFrame with generated data
    """
    print(f"Generating synthetic dataset from {start_date} to {end_date}...")
    rng = np.random.default_rng(random_state)
    
    # Generate dates
    dates = generate_dates(start_date, end_date)
    n_samples = len(dates)
    
    # Initialize data dictionary
    data = {
        'date': dates,
        'temperature': np.zeros(n_samples),
        'rainfall': np.zeros(n_samples),
        'humidity': np.zeros(n_samples),
        'holiday': np.zeros(n_samples, dtype=int),
        'weekend': np.zeros(n_samples, dtype=int),
        'population_density': np.zeros(n_samples),
        'event_level': np.zeros(n_samples, dtype=int),
        'waste_volume': np.zeros(n_samples)
    }
    
    # Base population density with gradual increase over years
    base_population = 8000
    
    for i, date in enumerate(dates):
        # Temperature (24-35 C with seasonal variation)
        month = date.month
        # Higher temp in dry season (Jun-Sep), lower in rainy season (Dec-Mar)
        seasonal_temp = 29.5 + 3.5 * np.sin((month - 1) * np.pi / 6)
        data['temperature'][i] = seasonal_temp + rng.normal(0, 1.5)
        data['temperature'][i] = np.clip(data['temperature'][i], 24, 35)
        
        # Rainfall (0-120mm, higher in rainy season)
        if month in [11, 12, 1, 2, 3]:  # Rainy season
            rainfall_mean = 40
            rainfall_std = 25
        else:  # Dry season
            rainfall_mean = 10
            rainfall_std = 8
        
        data['rainfall'][i] = max(0, rng.gamma(2, rainfall_mean/2) + rng.normal(0, rainfall_std))
        data['rainfall'][i] = min(data['rainfall'][i], 120)
        
        # Humidity (55-95%)
        # Higher humidity in rainy season and when there's rainfall
        base_humidity = 75
        if month in [11, 12, 1, 2, 3]:
            base_humidity = 82
        humidity = base_humidity + data['rainfall'][i] * 0.1 + rng.normal(0, 3)
        data['humidity'][i] = np.clip(humidity, 55, 95)
        
        # Holiday
        data['holiday'][i] = is_indonesian_holiday(date)
        
        # Weekend (Saturday=5, Sunday=6)
        data['weekend'][i] = 1 if date.weekday() >= 5 else 0
        
        # Population density (gradual increase over years)
        year_factor = (date.year - 2020) * 400  # 400 increase per year
        monthly_variation = rng.normal(0, 200)
        data['population_density'][i] = base_population + year_factor + monthly_variation
        data['population_density'][i] = np.clip(data['population_density'][i], 3000, 15000)
        
        # Event level (0-5, higher on weekends and holidays)
        base_event = rng.choice([0, 0, 0, 1, 1, 2], p=[0.4, 0.3, 0.15, 0.1, 0.04, 0.01])
        if data['weekend'][i] == 1:
            base_event = min(5, base_event + rng.choice([0, 1, 2], p=[0.3, 0.5, 0.2]))
        if data['holiday'][i] == 1:
            base_event = min(5, base_event + rng.choice([1, 2, 3], p=[0.4, 0.4, 0.2]))
        data['event_level'][i] = base_event
        
    # Generate waste volume based on all factors
    for i in range(n_samples):
        # Base waste volume from population density
        base_waste = data['population_density'][i] * 0.008  # ~64 tons for 8000 density
        
        # Weekend effect (+15% waste)
        weekend_effect = 1.15 if data['weekend'][i] == 1 else 1.0
        
        # Holiday effect (+25% waste)
        holiday_effect = 1.25 if data['holiday'][i] == 1 else 1.0
        
        # Event effect (up to +50% for level 5)
        event_effect = 1.0 + (data['event_level'][i] * 0.10)
        
        # Rainfall effect (slight decrease in waste when heavy rain)
        if data['rainfall'][i] > 50:
            rainfall_effect = 0.93
        elif data['rainfall'][i] > 20:
            rainfall_effect = 0.97
        else:
            rainfall_effect = 1.0
        
        # Temperature effect (minimal)
        temp_effect = 1.0 + (data['temperature'][i] - 29.5) * 0.005
        
        # Calculate waste volume
        waste = base_waste * weekend_effect * holiday_effect * event_effect * rainfall_effect * temp_effect
        
        # Add realistic noise
        noise = rng.normal(1.0, 0.04)  # 4% standard deviation
        waste = waste * noise
        
        # Seasonal trend (slightly more waste in certain months)
        month = dates[i].month
        if month in [12, 1, 6, 7]:  # Holiday seasons
            waste *= 1.08
        
        data['waste_volume'][i] = max(20, waste)  # Minimum 20 tons
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Format date as string
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    
    # Round numeric columns
    df['temperature'] = df['temperature'].round(1)
    df['rainfall'] = df['rainfall'].round(1)
    df['humidity'] = df['humidity'].round(1)
    df['population_density'] = df['population_density'].round(0).astype(int)
    df['waste_volume'] = df['waste_volume'].round(2)
    
    print(f"Generated {len(df)} samples")
    print(f"\nDataset statistics:")
    print(f"Waste volume range: {df['waste_volume'].min():.2f} - {df['waste_volume'].max():.2f} tons")
    print(f"Mean waste volume: {df['waste_volume'].mean():.2f} tons")
    print(f"Number of holidays: {df['holiday'].sum()}")
    print(f"Number of weekends: {df['weekend'].sum()}")
    
    # Save to CSV if path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"\nDataset saved to {output_path}")
    
    return df


if __name__ == "__main__":
    # Generate dataset
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent
    output_path = project_root / "data" / "raw" / "waste_dataset.csv"
    
    df = generate_waste_dataset(output_path=str(output_path))
    
    print("\nFirst 5 rows:")
    print(df.head())
    print("\nLast 5 rows:")
    print(df.tail())
