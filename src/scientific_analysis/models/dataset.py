"""
Dataset model for scientific data.
"""

from typing import Any, Dict, List, Optional, Union
import pandas as pd
import numpy as np

from .base_model import BaseModel


class Dataset(BaseModel):
    """Represents a dataset with metadata and data."""
    
    def __init__(
        self,
        data: Union[pd.DataFrame, np.ndarray, Dict, List],
        name: str = "Unnamed Dataset",
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a new dataset.
        
        Args:
            data: The dataset as a pandas DataFrame, NumPy array, dict, or list.
            name: Name of the dataset.
            description: Description of the dataset.
            metadata: Additional metadata as a dictionary.
        """
        self.name = name
        self.description = description
        self.metadata = metadata or {}
        self._data = self._ensure_dataframe(data)
    
    @property
    def data(self) -> pd.DataFrame:
        """Get the dataset as a pandas DataFrame."""
        return self._data
    
    @data.setter
    def data(self, value: Union[pd.DataFrame, np.ndarray, Dict, List]) -> None:
        """Set the dataset data."""
        self._data = self._ensure_dataframe(value)
    
    @property
    def shape(self) -> tuple:
        """Get the shape of the dataset (rows, columns)."""
        return self._data.shape
    
    @property
    def columns(self) -> List[str]:
        """Get the column names of the dataset."""
        return list(self._data.columns)
    
    @property
    def dtypes(self) -> Dict[str, str]:
        """Get the data types of each column."""
        return {col: str(dtype) for col, dtype in self._data.dtypes.items()}
    
    def head(self, n: int = 5) -> pd.DataFrame:
        """Get the first n rows of the dataset."""
        return self._data.head(n)
    
    def tail(self, n: int = 5) -> pd.DataFrame:
        """Get the last n rows of the dataset."""
        return self._data.tail(n)
    
    def describe(self) -> pd.DataFrame:
        """Generate descriptive statistics of the dataset."""
        return self._data.describe()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the dataset to a dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'metadata': self.metadata,
            'data': self._data.to_dict('records')
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Dataset':
        """Create a Dataset from a dictionary."""
        return cls(
            data=data.get('data', []),
            name=data.get('name', 'Unnamed Dataset'),
            description=data.get('description', ''),
            metadata=data.get('metadata', {})
        )
    
    def _ensure_dataframe(self, data: Any) -> pd.DataFrame:
        """Convert input data to a pandas DataFrame."""
        if isinstance(data, pd.DataFrame):
            return data.copy()
        elif isinstance(data, np.ndarray):
            return pd.DataFrame(data)
        elif isinstance(data, (dict, list)):
            return pd.DataFrame(data)
        else:
            raise ValueError(f"Unsupported data type: {type(data).__name__}")
    
    def __repr__(self) -> str:
        """String representation of the dataset."""
        return f"<Dataset(name='{self.name}', shape={self.shape})>"
