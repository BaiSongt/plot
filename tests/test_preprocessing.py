"""
Tests for the data preprocessing module.
"""

import unittest
import numpy as np
import pandas as pd
from scientific_analysis.data.preprocessing import DataPreprocessor, MissingValueStrategy, DataType, NormalizationMethod

class TestDataPreprocessor(unittest.TestCase):
    """Test cases for the DataPreprocessor class."""
    
    def setUp(self):
        """Set up test data."""
        self.test_data = {
            'A': [1, 2, np.nan, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e'],
            'C': [1.1, 2.2, 3.3, np.nan, 5.5],
            'D': [True, False, True, False, True]
        }
        self.df = pd.DataFrame(self.test_data)
    
    def test_handle_missing_values_drop(self):
        """Test dropping rows with missing values."""
        preprocessor = DataPreprocessor(self.df)
        preprocessor.handle_missing_values(strategy=MissingValueStrategy.DROP)
        result = preprocessor.get_processed_data()
        self.assertEqual(len(result), 3)  # Should have 3 rows after dropping
    
    def test_handle_missing_values_fill_mean(self):
        """Test filling missing values with mean."""
        preprocessor = DataPreprocessor(self.df)
        preprocessor.handle_missing_values(
            strategy=MissingValueStrategy.FILL_MEAN,
            columns=['A', 'C']
        )
        result = preprocessor.get_processed_data()
        self.assertFalse(result['A'].isna().any())
        self.assertFalse(result['C'].isna().any())
        # Calculate expected mean without NA values
        expected_mean = self.df['A'].dropna().mean()
        self.assertAlmostEqual(result['A'].mean(), expected_mean)
    
    def test_convert_dtypes(self):
        """Test data type conversion."""
        # Create a copy without NA values for this test
        df = self.df.dropna().copy()
        preprocessor = DataPreprocessor(df)
        preprocessor.convert_dtypes({
            'A': DataType.INTEGER,
            'B': DataType.CATEGORY,
            'C': DataType.FLOAT,
            'D': DataType.BOOLEAN
        })
        result = preprocessor.get_processed_data()
        # Accept both 'int64' and 'Int64' (pandas nullable integer)
        self.assertIn(str(result['A'].dtype), ['int64', 'Int64'])
        self.assertEqual(str(result['B'].dtype), 'category')
        self.assertEqual(str(result['C'].dtype), 'float64')
        self.assertEqual(str(result['D'].dtype), 'bool')
    
    def test_normalization(self):
        """Test data normalization."""
        preprocessor = DataPreprocessor(self.df)
        preprocessor.normalize(columns=['A', 'C'])
        result = preprocessor.get_processed_data()
        
        # Check if values are normalized (mean=0, std=1)
        self.assertAlmostEqual(result['A'].mean(), 0, delta=1e-10)
        self.assertAlmostEqual(result['C'].std(), 1, delta=1e-10)
    
    def test_detect_outliers(self):
        """Test outlier detection."""
        # Add an obvious outlier
        df = self.df.copy()
        df.loc[5] = [100, 'outlier', 1000.0, False]
        
        preprocessor = DataPreprocessor(df)
        is_outlier = preprocessor.detect_outliers(
            columns=['A', 'C'],
            method='zscore',
            threshold=2.0
        )
        
        # Only the last row should be an outlier
        self.assertTrue(is_outlier.iloc[-1])
        self.assertFalse(is_outlier.iloc[:-1].any())
    
    def test_filter_rows(self):
        """Test row filtering."""
        preprocessor = DataPreprocessor(self.df)
        preprocessor.filter_rows("A > 2")
        result = preprocessor.get_processed_data()
        
        # Only rows where A > 2 should remain (indices 2, 3, 4)
        self.assertEqual(len(result), 2)  # 4, 5 (index 3, 4)
        self.assertTrue((result['A'] > 2).all())
    
    def test_sample_data(self):
        """Test data sampling."""
        preprocessor = DataPreprocessor(self.df)
        preprocessor.sample_data(n=3, random_state=42)
        result = preprocessor.get_processed_data()
        
        # Should have exactly 3 rows
        self.assertEqual(len(result), 3)
        
        # Test with fraction
        preprocessor = DataPreprocessor(self.df)
        preprocessor.sample_data(frac=0.4, random_state=42)
        result = preprocessor.get_processed_data()
        
        # Should have 40% of rows (rounded)
        self.assertEqual(len(result), 2)  # 5 * 0.4 = 2


class TestMissingValueStrategy(unittest.TestCase):
    """Test cases for MissingValueStrategy enum."""
    
    def test_strategies(self):
        """Test all missing value strategies."""
        self.assertEqual(len(MissingValueStrategy), 6)
        self.assertEqual(MissingValueStrategy.DROP.value, 1)
        self.assertEqual(MissingValueStrategy.FILL_MEAN.value, 2)
        self.assertEqual(MissingValueStrategy.FILL_MEDIAN.value, 3)
        self.assertEqual(MissingValueStrategy.FILL_MODE.value, 4)
        self.assertEqual(MissingValueStrategy.FILL_VALUE.value, 5)
        self.assertEqual(MissingValueStrategy.INTERPOLATE.value, 6)


class TestDataType(unittest.TestCase):
    """Test cases for DataType enum."""
    
    def test_data_types(self):
        """Test all data types."""
        self.assertEqual(len(DataType), 6)
        self.assertEqual(DataType.INTEGER.value, 'int64')
        self.assertEqual(DataType.FLOAT.value, 'float64')
        self.assertEqual(DataType.STRING.value, 'object')
        self.assertEqual(DataType.CATEGORY.value, 'category')
        self.assertEqual(DataType.DATETIME.value, 'datetime64[ns]')
        self.assertEqual(DataType.BOOLEAN.value, 'bool')


class TestNormalizationMethod(unittest.TestCase):
    """Test cases for NormalizationMethod enum."""
    
    def test_methods(self):
        """Test all normalization methods."""
        self.assertEqual(len(NormalizationMethod), 4)
        self.assertEqual(NormalizationMethod.MIN_MAX.value, 'min_max')
        self.assertEqual(NormalizationMethod.STANDARD.value, 'standard')
        self.assertEqual(NormalizationMethod.ROBUST.value, 'robust')
        self.assertEqual(NormalizationMethod.MAX_ABS.value, 'max_abs')


if __name__ == '__main__':
    unittest.main()
