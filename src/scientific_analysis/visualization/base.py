"""可视化模块的基础类和接口

提供图表基类和图表类型枚举，作为所有可视化组件的基础。
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure


class ChartType(Enum):
    """图表类型枚举"""
    LINE = auto()       # 折线图
    BAR = auto()        # 柱状图
    SCATTER = auto()    # 散点图
    HISTOGRAM = auto()  # 直方图
    PIE = auto()        # 饼图
    BOX = auto()        # 箱线图
    HEATMAP = auto()    # 热图
    AREA = auto()       # 面积图
    VIOLIN = auto()     # 小提琴图
    RADAR = auto()      # 雷达图


class BaseChart:
    """所有图表类型的基类
    
    提供图表创建、配置和渲染的基本功能。
    """
    def __init__(self, data=None, title="", x_label="", y_label=""):
        """初始化图表
        
        Args:
            data: 图表数据，可以是DataFrame、NumPy数组或其他兼容格式
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
        """
        self.data = data
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.figure = None
        self.axes = None
        self.chart_type = None  # 子类应设置此属性
        
    def create_figure(self, figsize=(8, 6), dpi=100):
        """创建新的matplotlib图形
        
        Args:
            figsize: 图形大小，(宽度, 高度)，单位为英寸
            dpi: 分辨率，每英寸点数
            
        Returns:
            tuple: (figure, axes) - matplotlib图形和轴对象
        """
        self.figure = plt.figure(figsize=figsize, dpi=dpi)
        self.axes = self.figure.add_subplot(111)
        return self.figure, self.axes
        
    def set_title(self, title):
        """设置图表标题
        
        Args:
            title: 图表标题
        """
        self.title = title
        if self.axes:
            self.axes.set_title(title)
            
    def set_labels(self, x_label="", y_label=""):
        """设置坐标轴标签
        
        Args:
            x_label: X轴标签
            y_label: Y轴标签
        """
        self.x_label = x_label
        self.y_label = y_label
        if self.axes:
            self.axes.set_xlabel(x_label)
            self.axes.set_ylabel(y_label)
    
    def set_data(self, x_data, y_data):
        """设置图表数据
        
        Args:
            x_data: X轴数据
            y_data: Y轴数据
        """
        self.x = x_data
        self.y = y_data
        
    def plot(self):
        """绘制图表（由子类实现）
        
        Returns:
            Figure: matplotlib图形对象
        """
        raise NotImplementedError("子类必须实现plot()方法")
        
    def save(self, filename, dpi=300, **kwargs):
        """保存图表到文件
        
        Args:
            filename: 文件名
            dpi: 分辨率
            **kwargs: 传递给matplotlib的savefig的其他参数
            
        Returns:
            str: 保存的文件路径
        """
        if self.figure is None:
            self.plot()
            
        self.figure.savefig(filename, dpi=dpi, bbox_inches='tight', **kwargs)
        return filename
            
    def show(self):
        """显示图表"""
        if self.figure is None:
            self.plot()
            
        plt.show()
        
    def close(self):
        """关闭图表，释放资源"""
        if self.figure is not None:
            plt.close(self.figure)
            self.figure = None
            self.axes = None