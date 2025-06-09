"""
Complete data cleaning and preprocessing workflow example.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scientific_analysis.data import DataPreprocessor, MissingValueStrategy, DataType, NormalizationMethod

def load_sample_data():
    """Load sample data for demonstration."""
    # Create sample sales data with various data quality issues
    np.random.seed(42)
    
    dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
    n = len(dates)
    
    data = {
        'date': dates,
        'product_id': np.random.choice(['P001', 'P002', 'P003', 'P004', 'P005'], n),
        'category': np.random.choice(['Electronics', 'Clothing', 'Home', 'Books'], n),
        'price': np.random.uniform(10, 1000, n).round(2),
        'quantity': np.random.randint(1, 100, n),
        'rating': np.random.choice([1, 2, 3, 4, 5, np.nan], n, p=[0.05, 0.1, 0.15, 0.2, 0.45, 0.05]),
        'discount': np.random.choice([0, 0.1, 0.15, 0.2, 0.25, 0.3, np.nan], n, p=[0.6, 0.1, 0.1, 0.05, 0.05, 0.05, 0.05]),
        'is_featured': np.random.choice([True, False, np.nan], n, p=[0.3, 0.65, 0.05]),
        'customer_id': ['C{:04d}'.format(i) for i in np.random.randint(1, 501, n)],
        'region': np.random.choice(['North', 'South', 'East', 'West', np.nan], n, p=[0.25, 0.25, 0.25, 0.24, 0.01])
    }
    
    # Add some outliers
    outlier_indices = np.random.choice(n, size=int(n*0.02), replace=False)
    for idx in outlier_indices:
        if np.random.random() > 0.5:
            data['price'][idx] *= 10  # High price outlier
        else:
            data['quantity'][idx] *= 5  # High quantity outlier
    
    # Create DataFrame first
    df = pd.DataFrame(data)
    
    # Add some missing values
    for col in ['price', 'quantity', 'rating', 'discount']:
        missing_indices = np.random.choice(n, size=int(n*0.05), replace=False)
        if col in ['quantity']:  # For integer columns, use a sentinel value
            df[col] = df[col].astype(float)  # Convert to float to support NaN
        df.loc[df.index[missing_indices], col] = np.nan
    
    return df

def analyze_data(df):
    """Analyze and display data statistics."""
    print("\n=== Data Overview ===")
    print(f"Shape: {df.shape}")
    
    print("\n=== Data Types ===")
    print(df.dtypes)
    
    print("\n=== Missing Values ===")
    print(df.isna().sum())
    
    print("\n=== Basic Statistics ===")
    print(df.describe(include='all').T)

def plot_outliers(df, column):
    """Plot boxplot to visualize outliers."""
    plt.figure(figsize=(10, 6))
    df[column].plot(kind='box')
    plt.title(f'Boxplot of {column}')
    plt.show()

def main():
    # Load sample data
    print("Loading sample data...")
    df = load_sample_data()
    
    # Initial analysis
    print("Initial data analysis:")
    analyze_data(df)
    
    # Initialize preprocessor
    preprocessor = DataPreprocessor(df)
    
    # 1. Handle missing values
    print("\nHandling missing values...")
    preprocessor.handle_missing_values(
        strategy=MissingValueStrategy.FILL_MEAN,
        columns=['price', 'quantity']
    )
    preprocessor.handle_missing_values(
        strategy=MissingValueStrategy.FILL_MODE,
        columns=['rating', 'discount', 'is_featured', 'region']
    )
    
    # 2. Convert data types
    print("Converting data types...")
    preprocessor.convert_dtypes({
        'date': DataType.DATETIME,
        'product_id': DataType.CATEGORY,
        'category': DataType.CATEGORY,
        'is_featured': DataType.BOOLEAN,
        'customer_id': DataType.STRING,
        'region': DataType.CATEGORY
    })
    
    # 3. Handle outliers
    print("Handling outliers...")
    # First, let's see the outliers in price
    plot_outliers(df, 'price')
    
    # Remove outliers using IQR method
    preprocessor.remove_outliers(
        columns=['price', 'quantity'],
        method='iqr',
        threshold=1.5
    )
    
    # 4. Create new features
    print("Creating new features...")
    processed_df = preprocessor.get_processed_data()
    
    # Add total sales column
    processed_df['total_sales'] = processed_df['price'] * (1 - processed_df['discount'].fillna(0)) * processed_df['quantity']
    
    # Add month and day of week
    processed_df['month'] = processed_df['date'].dt.month_name()
    processed_df['day_of_week'] = processed_df['date'].dt.day_name()
    
    # 5. Normalize numeric columns
    print("Normalizing numeric columns...")
    preprocessor = DataPreprocessor(processed_df)
    preprocessor.normalize(
        columns=['price', 'quantity', 'total_sales'],
        method=NormalizationMethod.STANDARD
    )
    processed_df = preprocessor.get_processed_data()
    
    # Final analysis
    print("\nFinal data analysis:")
    analyze_data(processed_df)
    
    # Show sample of processed data
    print("\nSample of processed data:")
    print(processed_df.head())
    
    # Save processed data
    output_file = 'processed_sales_data.csv'
    processed_df.to_csv(output_file, index=False)
    print(f"\nProcessed data saved to {output_file}")

if __name__ == "__main__":
    main()
