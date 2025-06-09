"""
Configuration management for the Scientific Analysis Tool.
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = {
    "app": {
        "name": "Scientific Analysis Tool",
        "version": "0.1.0",
        "author": "",
        "email": ""
    },
    "ui": {
        "theme": "light",
        "font_size": 10,
        "recent_files": []
    },
    "data": {
        "default_directory": str(Path.home() / "Documents"),
        "auto_save": False,
        "auto_save_interval": 300
    },
    "plotting": {
        "default_style": "seaborn",
        "figure_size": [8, 6],
        "dpi": 100
    },
    "ai": {
        "enabled": False,
        "provider": "openai",
        "api_key": ""
    }
}

class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize the configuration manager.
        
        Args:
            config_file: Path to the configuration file. If None, uses the default location.
        """
        self.config_file = config_file or self.get_default_config_path()
        self.config = self._load_config()
    
    @staticmethod
    def get_default_config_path() -> str:
        """Get the default configuration file path.
        
        Returns:
            str: Path to the default configuration file.
        """
        config_dir = Path.home() / ".scientific_analysis"
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / "config.json")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create a default one.
        
        Returns:
            Dict[str, Any]: Loaded or default configuration.
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_file}")
                return self._merge_configs(DEFAULT_CONFIG, config)
            else:
                logger.info("No configuration file found, using defaults")
                return DEFAULT_CONFIG.copy()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            logger.info("Using default configuration")
            return DEFAULT_CONFIG.copy()
    
    def save_config(self) -> None:
        """Save the current configuration to file."""
        try:
            config_dir = os.path.dirname(self.config_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise
    
    @staticmethod
    def _merge_configs(default: Dict[str, Any], custom: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge two configuration dictionaries.
        
        Args:
            default: Default configuration.
            custom: Custom configuration to merge.
            
        Returns:
            Dict[str, Any]: Merged configuration.
        """
        result = default.copy()
        for key, value in custom.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigManager._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by dot-notation key.
        
        Args:
            key: Dot-notation key (e.g., "ui.theme").
            default: Default value if key is not found.
            
        Returns:
            Any: The configuration value or default.
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any, save: bool = True) -> None:
        """Set a configuration value by dot-notation key.
        
        Args:
            key: Dot-notation key (e.g., "ui.theme").
            value: Value to set.
            save: Whether to save the configuration after setting the value.
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        
        if save:
            self.save_config()
    
    def add_recent_file(self, file_path: str) -> None:
        """Add a file to the recent files list.
        
        Args:
            file_path: Path to the file to add.
        """
        recent_files = self.get('ui.recent_files', [])
        
        # Remove if already exists
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Add to the beginning
        recent_files.insert(0, file_path)
        
        # Keep only the last 10 files
        recent_files = recent_files[:10]
        
        self.set('ui.recent_files', recent_files)

# Global configuration instance
config = ConfigManager()
