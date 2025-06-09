"""
Base model class for data models in the Scientific Analysis Tool.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic, Type
import pandas as pd
import numpy as np

T = TypeVar('T', bound='BaseModel')

class BaseModel(ABC):
    """Base class for all data models in the application."""
    
    def __init__(self, **kwargs):
        """Initialize the model with keyword arguments."""
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    @abstractmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create a model instance from a dictionary.
        
        Args:
            data: Dictionary containing model data.
            
        Returns:
            An instance of the model.
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary.
        
        Returns:
            Dictionary representation of the model.
        """
        pass
    
    @classmethod
    def from_dataframe(cls: Type[T], df: pd.DataFrame) -> List[T]:
        """Create model instances from a pandas DataFrame.
        
        Args:
            df: Input DataFrame.
            
        Returns:
            List of model instances.
        """
        return [cls.from_dict(row.to_dict()) for _, row in df.iterrows()]
    
    @classmethod
    def to_dataframe(cls, items: List[T]) -> pd.DataFrame:
        """Convert a list of model instances to a pandas DataFrame.
        
        Args:
            items: List of model instances.
            
        Returns:
            DataFrame representation of the models.
        """
        return pd.DataFrame([item.to_dict() for item in items])
    
    def copy(self: T) -> T:
        """Create a deep copy of the model instance.
        
        Returns:
            A new instance with the same data.
        """
        return self.__class__(**self.to_dict())
    
    def __eq__(self, other: Any) -> bool:
        """Check if two model instances are equal."""
        if not isinstance(other, self.__class__):
            return False
        return self.to_dict() == other.to_dict()
    
    def __repr__(self) -> str:
        """Get a string representation of the model."""
        return f"{self.__class__.__name__}({self.to_dict()})"
