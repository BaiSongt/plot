"""
Data manager for handling dataset loading and saving operations.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple

import pandas as pd
import numpy as np
import h5py

from scientific_analysis.models import Dataset
from .io import DataIO

logger = logging.getLogger(__name__)


class DataManager:
    """Manages datasets and their persistence."""
    
    def __init__(self):
        """Initialize the data manager."""
        self._datasets: Dict[str, Dataset] = {}
        self._current_dataset: Optional[str] = None
        self._io = DataIO()
    
    @property
    def datasets(self) -> Dict[str, Dataset]:
        """Get all datasets."""
        return self._datasets.copy()
    
    @property
    def current_dataset(self) -> Optional[Dataset]:
        """Get the current active dataset."""
        if self._current_dataset is None:
            return None
        return self._datasets.get(self._current_dataset)
    
    def add_dataset(
        self, 
        dataset: Dataset, 
        name: Optional[str] = None,
        make_current: bool = True
    ) -> str:
        """Add a dataset to the manager.
        
        Args:
            dataset: The dataset to add.
            name: Optional name for the dataset. If None, uses dataset.name.
            make_current: Whether to make this the current dataset.
            
        Returns:
            str: The name under which the dataset was stored.
        """
        name = name or dataset.name
        
        # Ensure the name is unique
        base_name = name
        counter = 1
        while name in self._datasets:
            name = f"{base_name}_{counter}"
            counter += 1
        
        self._datasets[name] = dataset
        if make_current:
            self._current_dataset = name
        
        logger.info(f"Added dataset: {name}")
        return name
    
    def remove_dataset(self, name: str) -> bool:
        """Remove a dataset by name.
        
        Args:
            name: Name of the dataset to remove.
            
        Returns:
            bool: True if the dataset was removed, False otherwise.
        """
        if name in self._datasets:
            del self._datasets[name]
            if self._current_dataset == name:
                self._current_dataset = next(iter(self._datasets), None)
            logger.info(f"Removed dataset: {name}")
            return True
        return False
    
    def get_dataset(self, name: str) -> Optional[Dataset]:
        """Get a dataset by name.
        
        Args:
            name: Name of the dataset to get.
            
        Returns:
            Optional[Dataset]: The dataset if found, None otherwise.
        """
        return self._datasets.get(name)
    
    def get_dataset_names(self) -> List[str]:
        """Get all dataset names.
        
        Returns:
            List[str]: List of all dataset names.
        """
        return list(self._datasets.keys())
    
    def get_current_dataset(self) -> Optional[Dataset]:
        """Get the current active dataset.
        
        Returns:
            Optional[Dataset]: The current dataset if set, None otherwise.
        """
        return self.current_dataset
    
    def set_current_dataset(self, name: str) -> bool:
        """Set the current active dataset.
        
        Args:
            name: Name of the dataset to set as current.
            
        Returns:
            bool: True if the dataset was found and set as current, False otherwise.
        """
        if name in self._datasets:
            self._current_dataset = name
            return True
        return False
    
    def load_dataset(
        self, 
        file_path: Union[str, Path],
        name: Optional[str] = None,
        make_current: bool = True,
        **kwargs
    ) -> Optional[Dataset]:
        """Load a dataset from a file.
        
        Args:
            file_path: Path to the file to load.
            name: Optional name for the dataset. If None, uses the filename.
            make_current: Whether to make this the current dataset.
            **kwargs: Additional arguments passed to the data loader.
            
        Returns:
            Optional[Dataset]: The loaded dataset, or None if loading failed.
        """
        file_path = Path(file_path)
        
        try:
            # Read the file
            df, metadata = self._io.read_file(file_path, **kwargs)
            
            # Create a name if not provided
            if name is None:
                name = file_path.stem
            
            # Create and add the dataset
            dataset = Dataset(
                data=df,
                name=name,
                metadata={
                    'file_path': str(file_path.absolute()),
                    'file_format': metadata.get('file_format'),
                    **metadata
                }
            )
            
            # Add to manager
            self.add_dataset(dataset, name=name, make_current=make_current)
            
            return dataset
            
        except Exception as e:
            logger.error(f"Error loading dataset from {file_path}: {str(e)}", exc_info=True)
            return None
    
    def save_dataset(
        self,
        dataset: Optional[Union[Dataset, str]] = None,
        file_path: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> bool:
        """Save a dataset to a file.
        
        Args:
            dataset: The dataset to save, or its name. If None, uses the current dataset.
            file_path: Path to save the file to. If None, uses the dataset's file_path metadata.
            **kwargs: Additional arguments passed to the data saver.
            
        Returns:
            bool: True if the dataset was saved successfully, False otherwise.
        """
        # Get the dataset
        if dataset is None:
            dataset = self.current_dataset
        elif isinstance(dataset, str):
            dataset = self.get_dataset(dataset)
        
        if dataset is None:
            logger.error("No dataset to save")
            return False
        
        # Determine the file path
        if file_path is None:
            file_path = dataset.metadata.get('file_path')
            if file_path is None:
                logger.error("No file path provided and dataset has no saved path")
                return False
        
        file_path = Path(file_path)
        
        try:
            # Save the dataset
            metadata = self._io.write_file(dataset.data, file_path, **kwargs)
            
            # Update dataset metadata
            dataset.metadata.update({
                'file_path': str(file_path.absolute()),
                'file_format': metadata.get('file_format'),
                'last_saved': pd.Timestamp.now().isoformat()
            })
            
            logger.info(f"Saved dataset '{dataset.name}' to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving dataset to {file_path}: {str(e)}", exc_info=True)
            return False
    
    def import_from_clipboard(self, **kwargs) -> Optional[Dataset]:
        """Import data from the system clipboard.
        
        Args:
            **kwargs: Additional arguments passed to pandas.read_clipboard().
            
        Returns:
            Optional[Dataset]: The imported dataset, or None if import failed.
        """
        try:
            df = pd.read_clipboard(**kwargs)
            dataset = Dataset(data=df, name="Clipboard Data")
            self.add_dataset(dataset)
            return dataset
        except Exception as e:
            logger.error(f"Error importing from clipboard: {str(e)}", exc_info=True)
            return None
    
    def export_to_clipboard(self, dataset: Optional[Union[Dataset, str]] = None, **kwargs) -> bool:
        """Export a dataset to the system clipboard.
        
        Args:
            dataset: The dataset to export, or its name. If None, uses the current dataset.
            **kwargs: Additional arguments passed to DataFrame.to_clipboard().
            
        Returns:
            bool: True if the export was successful, False otherwise.
        """
        # Get the dataset
        if dataset is None:
            dataset = self.current_dataset
        elif isinstance(dataset, str):
            dataset = self.get_dataset(dataset)
        
        if dataset is None:
            logger.error("No dataset to export")
            return False
        
        try:
            dataset.data.to_clipboard(**kwargs)
            logger.info(f"Exported dataset '{dataset.name}' to clipboard")
            return True
        except Exception as e:
            logger.error(f"Error exporting to clipboard: {str(e)}", exc_info=True)
            return False
    
    def rename_dataset(self, old_name: str, new_name: str) -> bool:
        """Rename a dataset.
        
        Args:
            old_name: Current name of the dataset.
            new_name: New name for the dataset.
            
        Returns:
            bool: True if the dataset was renamed successfully, False otherwise.
        """
        if old_name not in self._datasets:
            logger.error(f"Dataset '{old_name}' not found")
            return False
            
        if new_name in self._datasets:
            logger.error(f"Dataset name '{new_name}' already exists")
            return False
            
        # Get the dataset and update its name
        dataset = self._datasets[old_name]
        dataset.name = new_name
        
        # Update the datasets dictionary
        self._datasets[new_name] = dataset
        del self._datasets[old_name]
        
        # Update current dataset reference if needed
        if self._current_dataset == old_name:
            self._current_dataset = new_name
            
        logger.info(f"Renamed dataset from '{old_name}' to '{new_name}'")
        return True
