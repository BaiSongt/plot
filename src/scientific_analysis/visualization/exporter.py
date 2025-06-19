"""图表导出功能

提供将图表导出为不同格式的功能，如PNG、JPG、SVG、PDF等。
"""

import os
from typing import Dict, List, Optional, Union, Any, Tuple
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
import pandas as pd

from .base import BaseChart


class ChartExporter:
    """图表导出器
    
    提供将图表导出为不同格式的功能。
    """
    
    # 支持的导出格式
    SUPPORTED_FORMATS = {
        'png': {'extension': '.png', 'description': 'PNG图像格式'},
        'jpg': {'extension': '.jpg', 'description': 'JPEG图像格式'},
        'svg': {'extension': '.svg', 'description': 'SVG矢量图格式'},
        'pdf': {'extension': '.pdf', 'description': 'PDF文档格式'},
        'eps': {'extension': '.eps', 'description': 'EPS矢量图格式'},
        'tif': {'extension': '.tif', 'description': 'TIFF图像格式'},
        'raw': {'extension': '.raw', 'description': '原始数据格式'},
        'csv': {'extension': '.csv', 'description': 'CSV数据格式'}
    }
    
    def __init__(self, chart: Optional[BaseChart] = None):
        """初始化图表导出器
        
        Args:
            chart: 要导出的图表对象，可选
        """
        self.chart = chart
        self.last_export_path = None
        
    def set_chart(self, chart: BaseChart) -> 'ChartExporter':
        """设置要导出的图表
        
        Args:
            chart: 图表对象
            
        Returns:
            ChartExporter: 返回自身，支持链式调用
        """
        self.chart = chart
        return self
        
    def export(self, filepath: str, format: str = None, dpi: int = 300, 
               transparent: bool = False, **kwargs) -> str:
        """导出图表为指定格式
        
        Args:
            filepath: 导出文件路径
            format: 导出格式，如果为None，则从文件扩展名推断
            dpi: 图像分辨率（仅对光栅图像格式有效）
            transparent: 是否使用透明背景
            **kwargs: 传递给matplotlib.figure.Figure.savefig的其他参数
            
        Returns:
            str: 导出文件的完整路径
            
        Raises:
            ValueError: 如果图表未设置或格式不支持
            IOError: 如果导出过程中发生IO错误
        """
        if self.chart is None or self.chart.figure is None:
            raise ValueError("未设置图表或图表未绘制")
            
        # 确保目录存在
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        # 如果未指定格式，从文件扩展名推断
        if format is None:
            _, ext = os.path.splitext(filepath)
            format = ext.lstrip('.').lower()
            
        # 检查格式是否支持
        if format not in self.SUPPORTED_FORMATS and format not in ['csv', 'raw']:
            raise ValueError(f"不支持的导出格式: {format}")
            
        # 根据格式导出
        if format in ['csv', 'raw']:
            return self._export_data(filepath, format, **kwargs)
        else:
            return self._export_figure(filepath, format, dpi, transparent, **kwargs)
            
    def _export_figure(self, filepath: str, format: str, dpi: int, 
                       transparent: bool, **kwargs) -> str:
        """导出图表为图像或文档格式
        
        Args:
            filepath: 导出文件路径
            format: 导出格式
            dpi: 图像分辨率
            transparent: 是否使用透明背景
            **kwargs: 其他参数
            
        Returns:
            str: 导出文件的完整路径
        """
        try:
            # 设置默认参数
            params = {
                'dpi': dpi,
                'transparent': transparent,
                'bbox_inches': 'tight'
            }
            params.update(kwargs)
            
            # 保存图表
            self.chart.figure.savefig(filepath, format=format, **params)
            self.last_export_path = filepath
            return filepath
        except Exception as e:
            raise IOError(f"导出图表时发生错误: {str(e)}")
            
    def _export_data(self, filepath: str, format: str, **kwargs) -> str:
        """导出图表的原始数据
        
        Args:
            filepath: 导出文件路径
            format: 导出格式 ('csv' 或 'raw')
            **kwargs: 其他参数
            
        Returns:
            str: 导出文件的完整路径
        """
        try:
            # 获取图表数据
            if not hasattr(self.chart, 'data') or self.chart.data is None:
                raise ValueError("图表没有可导出的数据")
                
            data = self.chart.data
            
            # 根据格式导出
            if format == 'csv':
                if isinstance(data, pd.DataFrame):
                    data.to_csv(filepath, **kwargs)
                elif isinstance(data, np.ndarray):
                    pd.DataFrame(data).to_csv(filepath, **kwargs)
                elif isinstance(data, dict):
                    pd.DataFrame(data).to_csv(filepath, **kwargs)
                else:
                    raise ValueError(f"不支持的数据类型: {type(data)}")
            elif format == 'raw':
                # 导出为原始格式（pickle或json）
                if isinstance(data, pd.DataFrame):
                    data.to_pickle(filepath)
                else:
                    import pickle
                    with open(filepath, 'wb') as f:
                        pickle.dump(data, f)
                        
            self.last_export_path = filepath
            return filepath
        except Exception as e:
            raise IOError(f"导出数据时发生错误: {str(e)}")
            
    def export_multiple_formats(self, base_filepath: str, formats: List[str], 
                               **kwargs) -> Dict[str, str]:
        """将图表导出为多种格式
        
        Args:
            base_filepath: 基础文件路径（不含扩展名）
            formats: 要导出的格式列表
            **kwargs: 传递给export方法的其他参数
            
        Returns:
            Dict[str, str]: 格式到文件路径的映射
        """
        results = {}
        for fmt in formats:
            if fmt not in self.SUPPORTED_FORMATS:
                print(f"警告: 不支持的格式 '{fmt}'，已跳过")
                continue
                
            ext = self.SUPPORTED_FORMATS[fmt]['extension']
            filepath = f"{base_filepath}{ext}"
            try:
                exported_path = self.export(filepath, fmt, **kwargs)
                results[fmt] = exported_path
            except Exception as e:
                print(f"导出格式 '{fmt}' 时发生错误: {str(e)}")
                
        return results
        
    def get_supported_formats(self) -> Dict[str, Dict[str, str]]:
        """获取支持的导出格式
        
        Returns:
            Dict[str, Dict[str, str]]: 支持的格式及其描述
        """
        return self.SUPPORTED_FORMATS
        
    def copy_to_clipboard(self) -> bool:
        """将图表复制到剪贴板
        
        Returns:
            bool: 是否成功复制到剪贴板
        """
        if self.chart is None or self.chart.figure is None:
            return False
            
        try:
            # 尝试复制到剪贴板
            from io import BytesIO
            buf = BytesIO()
            self.chart.figure.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            buf.seek(0)
            
            try:
                # 尝试使用PIL和pyperclip
                from PIL import Image
                import pyperclip
                image = Image.open(buf)
                
                # 复制到剪贴板
                if hasattr(image, 'copy'):
                    image.copy()
                    return True
                else:
                    print("警告: PIL Image对象没有copy方法")
                    return False
            except ImportError:
                print("警告: 复制到剪贴板需要PIL和pyperclip库")
                return False
        except Exception as e:
            print(f"复制到剪贴板时发生错误: {str(e)}")
            return False
            
    def open_exported_file(self) -> bool:
        """打开最近导出的文件
        
        Returns:
            bool: 是否成功打开文件
        """
        if not self.last_export_path or not os.path.exists(self.last_export_path):
            return False
            
        try:
            import subprocess
            import platform
            
            # 根据操作系统打开文件
            system = platform.system()
            if system == 'Windows':
                os.startfile(self.last_export_path)
            elif system == 'Darwin':  # macOS
                subprocess.call(['open', self.last_export_path])
            else:  # Linux
                subprocess.call(['xdg-open', self.last_export_path])
                
            return True
        except Exception as e:
            print(f"打开文件时发生错误: {str(e)}")
            return False