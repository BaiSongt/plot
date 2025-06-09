"""
Utility functions and classes for the Scientific Analysis Tool.
"""

from pathlib import Path
from typing import Optional

import pkg_resources

from scientific_analysis.config import config

def get_resource_path(relative_path: str) -> Path:
    """Get the absolute path to a resource file.
    
    Args:
        relative_path: Path relative to the package root.
        
    Returns:
        Path: Absolute path to the resource.
    """
    try:
        # Try to get the resource using pkg_resources
        return Path(pkg_resources.resource_filename('scientific_analysis', str(relative_path)))
    except Exception:
        # Fallback to direct path resolution
        return Path(__file__).parent.parent / relative_path


def ensure_directory_exists(directory: str) -> Path:
    """Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: Path to the directory.
        
    Returns:
        Path: Path object for the directory.
    """
    path = Path(directory).expanduser().absolute()
    path.mkdir(parents=True, exist_ok=True)
    return path
