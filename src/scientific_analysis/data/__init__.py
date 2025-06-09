"""
Data handling and processing for the Scientific Analysis Tool.
"""

from .io import DataIO
from .manager import DataManager
from .preprocessing import DataPreprocessor, MissingValueStrategy, DataType, NormalizationMethod

# Create a default instance for convenience
data_manager = DataManager()

__all__ = [
    'DataIO', 
    'DataManager', 
    'data_manager',
    'DataPreprocessor',
    'MissingValueStrategy',
    'DataType',
    'NormalizationMethod'
]
