"""
Data import/export functionality for the Scientific Analysis Tool.
"""

import os
import json
import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
import pandas as pd
import h5py
import numpy as np

from scientific_analysis.config import config
from scientific_analysis.utils import ensure_directory_exists

class DataIO:
    """Handles data import and export operations."""
    
    SUPPORTED_FORMATS = {
        'csv': ('Comma-Separated Values', '.csv'),
        'excel': ('Excel', '.xlsx'),
        'json': ('JSON', '.json'),
        'hdf5': ('HDF5', '.h5'),
        'parquet': ('Parquet', '.parquet'),
        'feather': ('Feather', '.feather')
    }
    
    @classmethod
    def get_supported_formats(cls) -> Dict[str, str]:
        """Get a dictionary of supported file formats and their extensions.
        
        Returns:
            Dict[str, str]: Format name to extension mapping.
        """
        return {k: v[1] for k, v in cls.SUPPORTED_FORMATS.items()}
    
    @classmethod
    def get_file_filters(cls) -> str:
        """Get file filters for file dialogs.
        
        Returns:
            str: File filters string.
        """
        filters = []
        all_extensions = []
        
        for fmt, (name, ext) in cls.SUPPORTED_FORMATS.items():
            filter_str = f"{name} (*{ext})"
            filters.append(filter_str)
            all_extensions.append(f"*{ext}")
        
        # Add "All Supported Files" filter
        all_filter = f"All Supported Files ({' '.join(all_extensions)})"
        filters.insert(0, all_filter)
        
        # Add "All Files" filter
        filters.append("All Files (*)")
        
        return ";;".join(filters)
    
    @classmethod
    def detect_format(cls, file_path: Union[str, Path]) -> Optional[str]:
        """Detect the format of a file based on its extension.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            str: Format name or None if not supported.
        """
        file_path = Path(file_path)
        ext = file_path.suffix.lower()
        
        for fmt, (_, format_ext) in cls.SUPPORTED_FORMATS.items():
            if ext == format_ext.lower():
                return fmt
        
        return None
    
    @classmethod
    def read_file(cls, file_path: Union[str, Path], **kwargs) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Read data from a file.
        
        Args:
            file_path: Path to the file.
            **kwargs: Additional arguments passed to the underlying reader.
            
        Returns:
            Tuple containing:
                - DataFrame with the data
                - Dictionary with metadata
            
        Raises:
            ValueError: If the file format is not supported or reading fails.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_format = cls.detect_format(file_path)
        if file_format is None:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        try:
            if file_format == 'csv':
                df = pd.read_csv(file_path, **kwargs)
            elif file_format == 'excel':
                df = pd.read_excel(file_path, **kwargs)
            elif file_format == 'json':
                df = pd.read_json(file_path, **kwargs)
            elif file_format == 'hdf5':
                with h5py.File(file_path, 'r') as f:
                    # Get the first dataset in the file
                    dataset_name = list(f.keys())[0]
                    data = f[dataset_name][:]
                    df = pd.DataFrame(data)
            elif file_format == 'parquet':
                df = pd.read_parquet(file_path, **kwargs)
            elif file_format == 'feather':
                df = pd.read_feather(file_path, **kwargs)
            else:
                raise ValueError(f"Unsupported format: {file_format}")
            
            # Update recent files in config
            config.add_recent_file(str(file_path.absolute()))
            
            # Prepare metadata
            metadata = {
                'file_path': str(file_path.absolute()),
                'file_format': file_format,
                'num_rows': len(df),
                'num_columns': len(df.columns),
                'columns': list(df.columns),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
            }
            
            return df, metadata
            
        except Exception as e:
            raise ValueError(f"Error reading {file_path}: {str(e)}")
    
    @classmethod
    def write_file(
        cls, 
        df: pd.DataFrame, 
        file_path: Union[str, Path], 
        file_format: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Write data to a file.
        
        Args:
            df: DataFrame to save.
            file_path: Path to save the file to.
            file_format: Format to save as. If None, inferred from file extension.
            **kwargs: Additional arguments passed to the underlying writer.
            
        Returns:
            Dictionary with metadata about the saved file.
            
        Raises:
            ValueError: If the file format is not supported or writing fails.
        """
        file_path = Path(file_path)
        
        if file_format is None:
            file_format = cls.detect_format(file_path)
            if file_format is None:
                raise ValueError(
                    f"Could not determine file format from extension: {file_path.suffix}"
                )
        
        # Ensure the directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if file_format == 'csv':
                df.to_csv(file_path, index=False, **kwargs)
            elif file_format == 'excel':
                df.to_excel(file_path, index=False, **kwargs)
            elif file_format == 'json':
                df.to_json(file_path, orient='records', lines=False, **kwargs)
            elif file_format == 'hdf5':
                with h5py.File(file_path, 'w') as f:
                    f.create_dataset('data', data=df.to_records(index=False))
            elif file_format == 'parquet':
                df.to_parquet(file_path, index=False, **kwargs)
            elif file_format == 'feather':
                df.to_feather(file_path, **kwargs)
            else:
                raise ValueError(f"Unsupported format: {file_format}")
            
            # Update recent files in config
            config.add_recent_file(str(file_path.absolute()))
            
            # Prepare metadata
            metadata = {
                'file_path': str(file_path.absolute()),
                'file_format': file_format,
                'num_rows': len(df),
                'num_columns': len(df.columns),
                'columns': list(df.columns),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
            }
            
            return metadata
            
        except Exception as e:
            raise ValueError(f"Error writing to {file_path}: {str(e)}")
    
    @classmethod
    def export_figure(
        cls, 
        fig: 'matplotlib.figure.Figure', 
        file_path: Union[str, Path], 
        dpi: int = 300,
        **kwargs
    ) -> Dict[str, Any]:
        """Export a matplotlib figure to a file.
        
        Args:
            fig: Matplotlib figure to export.
            file_path: Path to save the figure to.
            dpi: Resolution in dots per inch.
            **kwargs: Additional arguments passed to savefig.
            
        Returns:
            Dictionary with metadata about the saved figure.
        """
        import matplotlib.pyplot as plt
        
        file_path = Path(file_path)
        file_format = file_path.suffix[1:].lower()  # Remove the dot
        
        supported_formats = plt.gcf().canvas.get_supported_filetypes()
        if file_format not in supported_formats:
            raise ValueError(
                f"Unsupported image format: {file_format}. "
                f"Supported formats: {', '.join(supported_formats.keys())}"
            )
        
        # Ensure the directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            fig.savefig(
                file_path, 
                dpi=dpi, 
                bbox_inches='tight',
                **kwargs
            )
            
            # Prepare metadata
            metadata = {
                'file_path': str(file_path.absolute()),
                'format': file_format,
                'dpi': dpi,
                'size_inches': fig.get_size_inches().tolist(),
                'axes_count': len(fig.axes)
            }
            
            return metadata
            
        except Exception as e:
            raise ValueError(f"Error saving figure to {file_path}: {str(e)}")
