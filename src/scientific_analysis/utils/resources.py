"""
Resource management for the Scientific Analysis Tool.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Union

from PySide6.QtGui import QIcon, QPixmap, QFont, QFontDatabase
from PySide6.QtWidgets import QApplication

from scientific_analysis.config import config


class ResourceManager:
    """Manages application resources like icons, images, and fonts."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._icon_cache = {}
        self._font_cache = {}
        self._resource_dirs = {
            'icons': 'resources/icons',
            'images': 'resources/images',
            'fonts': 'resources/fonts',
            'styles': 'resources/styles'
        }
        
        # Create resource directories if they don't exist
        self._ensure_resource_directories()
    
    def _ensure_resource_directories(self) -> None:
        """Ensure all resource directories exist."""
        for dir_type, rel_path in self._resource_dirs.items():
            abs_path = self.get_resource_path(rel_path)
            abs_path.mkdir(parents=True, exist_ok=True)
    
    def get_resource_path(self, relative_path: str) -> Path:
        """Get the absolute path to a resource file.
        
        Args:
            relative_path: Path relative to the resources directory.
            
        Returns:
            Path: Absolute path to the resource.
        """
        # First try to find the resource in the package
        try:
            import pkg_resources
            return Path(pkg_resources.resource_filename('scientific_analysis', str(relative_path)))
        except Exception:
            # Fallback to direct path resolution
            return Path(__file__).parent.parent.parent / relative_path
    
    def get_icon(self, name: str, color: Optional[str] = None) -> QIcon:
        """Get an icon by name.
        
        Args:
            name: Icon name without extension.
            color: Optional color to apply to the icon.
            
        Returns:
            QIcon: The requested icon.
        """
        cache_key = f"{name}_{color if color else 'default'}"
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]
        
        # Look for the icon in the resources directory
        icon_path = self.get_resource_path(f"resources/icons/{name}.svg")
        
        if not icon_path.exists():
            # Fall back to a default icon if the requested one doesn't exist
            icon_path = self.get_resource_path("resources/icons/default_icon.svg")
            if not icon_path.exists():
                # If no default icon exists, return a blank icon
                return QIcon()
        
        icon = QIcon(str(icon_path))
        
        if color:
            # Apply color to the icon if specified
            pixmap = icon.pixmap(32, 32)
            if not pixmap.isNull():
                from PySide6.QtGui import QPainter
                from PySide6.QtCore import Qt
                
                colored_pixmap = QPixmap(pixmap.size())
                colored_pixmap.fill(Qt.transparent)
                
                painter = QPainter(colored_pixmap)
                painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                painter.drawPixmap(0, 0, pixmap)
                
                # Apply color to non-transparent pixels
                painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
                painter.fillRect(pixmap.rect(), color)
                painter.end()
                
                icon = QIcon(colored_pixmap)
        
        self._icon_cache[cache_key] = icon
        return icon
    
    def get_pixmap(self, name: str) -> QPixmap:
        """Get a pixmap by name.
        
        Args:
            name: Image name without extension.
            
        Returns:
            QPixmap: The requested pixmap.
        """
        image_path = self.get_resource_path(f"resources/images/{name}.png")
        if not image_path.exists():
            image_path = self.get_resource_path(f"resources/images/{name}.jpg")
        
        if image_path.exists():
            return QPixmap(str(image_path))
        
        # Return an empty pixmap if the image doesn't exist
        return QPixmap()
    
    def load_fonts(self) -> None:
        """Load custom fonts from the resources directory."""
        fonts_dir = self.get_resource_path("resources/fonts")
        
        if not fonts_dir.exists():
            return
        
        # Supported font extensions
        extensions = ('.ttf', '.otf')
        
        # Load all font files in the directory
        for font_file in fonts_dir.glob('*'):
            if font_file.suffix.lower() in extensions:
                font_id = QFontDatabase.addApplicationFont(str(font_file))
                if font_id != -1:
                    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                    self._font_cache[font_file.stem] = font_family
    
    def get_font(self, family: str, point_size: int = -1, weight: int = -1, italic: bool = False) -> QFont:
        """Get a font by family name.
        
        Args:
            family: Font family name.
            point_size: Font size in points.
            weight: Font weight.
            italic: Whether the font should be italic.
            
        Returns:
            QFont: The requested font.
        """
        # Try to get the font from the cache
        font_family = self._font_cache.get(family, family)
        font = QFont(font_family, point_size, weight, italic)
        return font
    
    def get_style_sheet(self, name: str = 'default') -> str:
        """Get a style sheet by name.
        
        Args:
            name: Style sheet name without extension.
            
        Returns:
            str: The style sheet content.
        """
        style_path = self.get_resource_path(f"resources/styles/{name}.qss")
        
        if not style_path.exists():
            return ""
        
        try:
            with open(style_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading style sheet {name}: {e}")
            return ""


# Global resource manager instance
resources = ResourceManager()


def init_resources() -> None:
    """Initialize application resources."""
    # Load custom fonts
    resources.load_fonts()
    
    # Apply default style sheet
    app = QApplication.instance()
    if app is not None:
        style = resources.get_style_sheet('default')
        if style:
            app.setStyleSheet(style)
