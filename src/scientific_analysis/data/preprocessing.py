"""
Data preprocessing utilities for the Scientific Analysis Tool.
"""

from typing import Union, List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from enum import Enum, auto


class MissingValueStrategy(Enum):
    """Strategies for handling missing values."""
    DROP = auto()
    FILL_MEAN = auto()
    FILL_MEDIAN = auto()
    FILL_MODE = auto()
    FILL_VALUE = auto()
    INTERPOLATE = auto()


class DataType(Enum):
    """Supported data types for conversion."""
    INTEGER = 'int64'
    FLOAT = 'float64'
    STRING = 'object'
    CATEGORY = 'category'
    DATETIME = 'datetime64[ns]'
    BOOLEAN = 'bool'


class NormalizationMethod(Enum):
    """Normalization methods."""
    MIN_MAX = 'min_max'
    STANDARD = 'standard'
    ROBUST = 'robust'
    MAX_ABS = 'max_abs'


class DataPreprocessor:
    """A class for preprocessing data in a DataFrame."""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize with a pandas DataFrame."""
        self.df = df.copy()
        self._original_dtypes = df.dtypes.to_dict()
    
    def handle_missing_values(self, 
                            strategy: Union[str, MissingValueStrategy] = MissingValueStrategy.DROP,
                            columns: List[str] = None,
                            fill_value: Any = None) -> 'DataPreprocessor':
        """Handle missing values in the DataFrame.
        
        Args:
            strategy: Strategy to use for handling missing values.
            columns: List of columns to process. If None, process all columns.
            fill_value: Value to use when strategy is FILL_VALUE.
            
        Returns:
            self for method chaining.
        """
        if isinstance(strategy, str):
            strategy = MissingValueStrategy[str.upper(strategy)]
        
        columns = columns or self.df.columns.tolist()
        
        for col in columns:
            if col not in self.df.columns:
                continue
                
            if self.df[col].isna().any():
                if strategy == MissingValueStrategy.DROP:
                    self.df = self.df.dropna(subset=[col])
                elif strategy == MissingValueStrategy.FILL_MEAN:
                    self.df[col] = self.df[col].fillna(self.df[col].mean())
                elif strategy == MissingValueStrategy.FILL_MEDIAN:
                    self.df[col] = self.df[col].fillna(self.df[col].median())
                elif strategy == MissingValueStrategy.FILL_MODE:
                    self.df[col] = self.df[col].fillna(self.df[col].mode()[0])
                elif strategy == MissingValueStrategy.FILL_VALUE:
                    if fill_value is None:
                        raise ValueError("fill_value must be provided when using FILL_VALUE strategy")
                    self.df[col] = self.df[col].fillna(fill_value)
                elif strategy == MissingValueStrategy.INTERPOLATE:
                    self.df[col] = self.df[col].interpolate()
        
        return self
    
    def convert_dtypes(self, 
                      dtype_map: Dict[str, Union[str, DataType]] = None,
                      infer_objects: bool = True) -> 'DataPreprocessor':
        """Convert data types of columns.
        
        Args:
            dtype_map: Dictionary mapping column names to target data types.
            infer_objects: Whether to infer object dtypes.
            
        Returns:
            self for method chaining.
        """
        if dtype_map:
            for col, dtype in dtype_map.items():
                if col in self.df.columns:
                    if isinstance(dtype, DataType):
                        self.df[col] = self.df[col].astype(dtype.value)
                    else:
                        self.df[col] = self.df[col].astype(dtype)
        
        if infer_objects:
            self.df = self.df.infer_objects()
            
        return self
    
    def normalize(self, 
                 columns: List[str] = None,
                 method: Union[str, NormalizationMethod] = NormalizationMethod.STANDARD,
                 inplace: bool = True) -> 'DataPreprocessor':
        """Normalize numeric columns.
        
        Args:
            columns: Columns to normalize. If None, normalize all numeric columns.
            method: Normalization method to use.
            inplace: Whether to modify the DataFrame in place.
            
        Returns:
            self for method chaining.
        """
        if isinstance(method, str):
            method = NormalizationMethod(method.lower())
        
        numeric_cols = self.df.select_dtypes(include=['number']).columns
        columns = columns or numeric_cols
        
        # Filter to only include columns that exist and are numeric
        columns = [col for col in columns if col in numeric_cols]
        
        if not columns:
            return self
            
        df_to_normalize = self.df[columns].copy()
        
        if method == NormalizationMethod.MIN_MAX:
            normalized = (df_to_normalize - df_to_normalize.min()) / \
                       (df_to_normalize.max() - df_to_normalize.min())
        elif method == NormalizationMethod.STANDARD:
            normalized = (df_to_normalize - df_to_normalize.mean()) / df_to_normalize.std()
        elif method == NormalizationMethod.ROBUST:
            normalized = (df_to_normalize - df_to_normalize.median()) / \
                       (df_to_normalize.quantile(0.75) - df_to_normalize.quantile(0.25))
        elif method == NormalizationMethod.MAX_ABS:
            normalized = df_to_normalize / df_to_normalize.abs().max()
        else:
            raise ValueError(f"Unsupported normalization method: {method}")
        
        if inplace:
            self.df[columns] = normalized
        else:
            return normalized
            
        return self
    
    def detect_outliers(self, 
                    columns: List[str] = None,
                    method: str = 'zscore',
                    threshold: float = 3.0) -> pd.Series:
        """Detect outliers in numeric columns.
        
        Args:
            columns: Columns to check for outliers.
            method: Method to use ('zscore' or 'iqr').
            threshold: Threshold for considering a value an outlier.
            
        Returns:
            Boolean Series indicating outlier positions.
        """
        # Get numeric columns if none specified
        numeric_cols = self.df.select_dtypes(include=['number']).columns
        columns = columns or numeric_cols
        
        # Ensure columns exist in the DataFrame
        columns = [col for col in columns if col in self.df.columns and col in numeric_cols]
        
        if not columns:
            return pd.Series(False, index=self.df.index)
        
        # Create a copy of the dataframe for calculations to avoid modifying original
        df_calc = self.df[columns].copy()
        
        # Initialize result series with False
        is_outlier = pd.Series(False, index=self.df.index)
        
        if method == 'zscore':
            # Calculate z-scores for each column, handling NaN values
            for col in columns:
                # Skip columns with all NaN values
                if df_calc[col].isna().all():
                    continue
                    
                # Calculate mean and std without NaN values
                mean = df_calc[col].mean()
                std = df_calc[col].std()
                
                # Skip if std is zero (all values are the same)
                if std == 0:
                    continue
                    
                # Calculate z-scores
                z_scores = (df_calc[col] - mean) / std
                
                # Update outlier flags
                is_outlier = is_outlier | (z_scores.abs() > threshold)
                
        elif method == 'iqr':
            # Calculate IQR for each column
            for col in columns:
                # Skip columns with all NaN values
                if df_calc[col].isna().all():
                    continue
                    
                q1 = df_calc[col].quantile(0.25)
                q3 = df_calc[col].quantile(0.75)
                iqr = q3 - q1
                
                # Skip if IQR is zero
                if iqr == 0:
                    continue
                    
                lower_bound = q1 - (threshold * iqr)
                upper_bound = q3 + (threshold * iqr)
                
                # Update outlier flags
                is_outlier = is_outlier | ((df_calc[col] < lower_bound) | (df_calc[col] > upper_bound))
        else:
            raise ValueError(f"Unsupported outlier detection method: {method}")
        
        # Convert to Python bool to avoid numpy bool issues in assertions
        return pd.Series([bool(x) for x in is_outlier], index=self.df.index)
    
    def remove_outliers(self, 
                       columns: List[str] = None,
                       method: str = 'zscore',
                       threshold: float = 3.0) -> 'DataPreprocessor':
        """Remove rows containing outliers.
        
        Args:
            columns: Columns to check for outliers.
            method: Method to use ('zscore' or 'iqr').
            threshold: Threshold for considering a value an outlier.
            
        Returns:
            self for method chaining.
        """
        is_outlier = self.detect_outliers(columns, method, threshold)
        self.df = self.df[~is_outlier].copy()
        return self
    
    def filter_rows(self, condition: str) -> 'DataPreprocessor':
        """Filter rows based on a query string.
        
        Args:
            condition: Query string to evaluate.
            
        Returns:
            self for method chaining.
        """
        self.df = self.df.query(condition).copy()
        return self
    
    def sample_data(self, 
                   n: int = None, 
                   frac: float = None, 
                   random_state: int = None) -> 'DataPreprocessor':
        """Sample rows from the DataFrame.
        
        Args:
            n: Number of samples to return.
            frac: Fraction of rows to return.
            random_state: Random seed for reproducibility.
            
        Returns:
            self for method chaining.
        """
        if n is not None or frac is not None:
            self.df = self.df.sample(n=n, frac=frac, random_state=random_state).copy()
        return self
    
    def get_processed_data(self) -> pd.DataFrame:
        """Get the processed DataFrame.
        
        Returns:
            The processed pandas DataFrame.
        """
        return self.df.copy()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the preprocessing operations.
        
        Returns:
            Dictionary containing summary information.
        """
        return {
            'original_shape': (len(self.df), len(self._original_dtypes)),
            'current_shape': self.df.shape,
            'missing_values': int(self.df.isna().sum().sum()),
            'dtypes': self.df.dtypes.astype(str).to_dict(),
            'numeric_columns': self.df.select_dtypes(include=['number']).columns.tolist(),
            'categorical_columns': self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        }
