"""基本图表类型实现

提供各种基本图表类型的实现，包括折线图、柱状图、散点图、直方图和饼图等。
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .base import BaseChart, ChartType


class LineChart(BaseChart):
    """折线图实现"""
    
    def __init__(self, data=None, x=None, y=None, **kwargs):
        """初始化折线图
        
        Args:
            data: 图表数据
            x: X轴数据列名或数据
            y: Y轴数据列名或数据
            **kwargs: 传递给BaseChart的其他参数
        """
        super().__init__(data, **kwargs)
        self.x = x
        self.y = y
        self.chart_type = ChartType.LINE
        
    def plot(self):
        """绘制折线图
        
        Returns:
            Figure: matplotlib图形对象
        """
        if self.figure is None:
            self.create_figure()
            
        if isinstance(self.data, pd.DataFrame):
            if self.x is not None and self.y is not None:
                self.data.plot(kind='line', x=self.x, y=self.y, ax=self.axes)
            else:
                self.data.plot(kind='line', ax=self.axes)
        elif isinstance(self.data, (list, np.ndarray)):
            x_data = range(len(self.data)) if self.x is None else self.x
            y_data = self.data if self.y is None else self.y
            self.axes.plot(x_data, y_data)
            
        self.set_title(self.title)
        self.set_labels(self.x_label, self.y_label)
        self.figure.tight_layout()
        return self.figure


class BarChart(BaseChart):
    """柱状图实现"""
    
    def __init__(self, data=None, x=None, y=None, orientation='vertical', **kwargs):
        """初始化柱状图
        
        Args:
            data: 图表数据
            x: X轴数据列名或数据
            y: Y轴数据列名或数据
            orientation: 方向，'vertical'为垂直柱状图，'horizontal'为水平柱状图
            **kwargs: 传递给BaseChart的其他参数
        """
        super().__init__(data, **kwargs)
        self.x = x
        self.y = y
        self.orientation = orientation
        self.chart_type = ChartType.BAR
        
    def plot(self):
        """绘制柱状图
        
        Returns:
            Figure: matplotlib图形对象
        """
        if self.figure is None:
            self.create_figure()
            
        kind = 'bar' if self.orientation == 'vertical' else 'barh'
            
        if isinstance(self.data, pd.DataFrame):
            if self.x is not None and self.y is not None:
                self.data.plot(kind=kind, x=self.x, y=self.y, ax=self.axes)
            else:
                self.data.plot(kind=kind, ax=self.axes)
        elif isinstance(self.data, (list, np.ndarray)):
            x_data = range(len(self.data)) if self.x is None else self.x
            y_data = self.data if self.y is None else self.y
            
            if kind == 'bar':
                self.axes.bar(x_data, y_data)
            else:
                self.axes.barh(x_data, y_data)
            
        self.set_title(self.title)
        self.set_labels(self.x_label, self.y_label)
        self.figure.tight_layout()
        return self.figure


class ScatterChart(BaseChart):
    """散点图实现"""
    
    def __init__(self, data=None, x=None, y=None, c=None, s=None, **kwargs):
        """初始化散点图
        
        Args:
            data: 图表数据
            x: X轴数据列名或数据
            y: Y轴数据列名或数据
            c: 点颜色数据列名或数据
            s: 点大小数据列名或数据
            **kwargs: 传递给BaseChart的其他参数
        """
        super().__init__(data, **kwargs)
        self.x = x
        self.y = y
        self.c = c  # 颜色映射列
        self.s = s  # 大小映射列
        self.chart_type = ChartType.SCATTER
        
    def set_data(self, x_data, y_data, c_data=None, s_data=None):
        """设置散点图数据
        
        Args:
            x_data: X轴数据
            y_data: Y轴数据
            c_data: 点颜色数据
            s_data: 点大小数据
        """
        self.x = x_data
        self.y = y_data
        self.c = c_data
        self.s = s_data
        
    def plot(self):
        """绘制散点图
        
        Returns:
            Figure: matplotlib图形对象
        """
        if self.figure is None:
            self.create_figure()
            
        if isinstance(self.data, pd.DataFrame):
            if self.x is not None and self.y is not None:
                # 处理颜色和大小映射
                c_data = self.data[self.c] if self.c is not None else None
                s_data = self.data[self.s] if self.s is not None else None
                
                scatter = self.axes.scatter(
                    self.data[self.x], 
                    self.data[self.y],
                    c=c_data,
                    s=s_data
                )
                
                # 如果有颜色映射，添加颜色条
                if c_data is not None:
                    self.figure.colorbar(scatter, ax=self.axes)
            else:
                self.data.plot.scatter(ax=self.axes)
        elif isinstance(self.data, (list, np.ndarray)):
            x_data = range(len(self.data)) if self.x is None else self.x
            y_data = self.data if self.y is None else self.y
            self.axes.scatter(x_data, y_data)
            
        self.set_title(self.title)
        self.set_labels(self.x_label, self.y_label)
        self.figure.tight_layout()
        return self.figure


class HistogramChart(BaseChart):
    """直方图实现"""
    
    def __init__(self, data=None, column=None, bins=10, **kwargs):
        """初始化直方图
        
        Args:
            data: 图表数据
            column: 要绘制直方图的列名
            bins: 直方图的箱数
            **kwargs: 传递给BaseChart的其他参数
        """
        super().__init__(data, **kwargs)
        self.column = column
        self.bins = bins
        self.chart_type = ChartType.HISTOGRAM
        
    def plot(self):
        """绘制直方图
        
        Returns:
            Figure: matplotlib图形对象
        """
        if self.figure is None:
            self.create_figure()
            
        if isinstance(self.data, pd.DataFrame):
            if self.column is not None:
                self.data[self.column].plot.hist(bins=self.bins, ax=self.axes)
            else:
                self.data.plot.hist(bins=self.bins, ax=self.axes)
        elif isinstance(self.data, (list, np.ndarray)):
            self.axes.hist(self.data, bins=self.bins)
            
        self.set_title(self.title)
        self.set_labels(self.x_label, self.y_label)
        self.figure.tight_layout()
        return self.figure


class PieChart(BaseChart):
    """饼图实现"""
    
    def __init__(self, data=None, values=None, labels=None, **kwargs):
        """初始化饼图
        
        Args:
            data: 图表数据
            values: 值列名或数据
            labels: 标签列名或数据
            **kwargs: 传递给BaseChart的其他参数
        """
        super().__init__(data, **kwargs)
        self.values = values
        self.labels = labels
        self.chart_type = ChartType.PIE
        
    def plot(self):
        """绘制饼图
        
        Returns:
            Figure: matplotlib图形对象
        """
        if self.figure is None:
            self.create_figure()
            
        if isinstance(self.data, pd.DataFrame):
            if self.values is not None:
                if self.labels is not None:
                    self.data.plot.pie(
                        y=self.values, 
                        labels=self.data[self.labels], 
                        ax=self.axes
                    )
                else:
                    self.data.plot.pie(y=self.values, ax=self.axes)
            elif self.labels is not None:
                # 使用标签列作为索引，值为1的Series
                pd.Series(1, index=self.data[self.labels]).plot.pie(ax=self.axes)
            else:
                self.data.plot.pie(ax=self.axes)
        elif isinstance(self.data, (list, np.ndarray)):
            self.axes.pie(
                self.data, 
                labels=self.labels if self.labels is not None else None,
                autopct='%1.1f%%'
            )
            
        self.set_title(self.title)
        self.axes.axis('equal')  # 确保饼图是圆形的
        self.figure.tight_layout()
        return self.figure


class BoxPlot(BaseChart):
    """箱线图实现"""
    
    def __init__(self, data=None, column=None, by=None, **kwargs):
        """初始化箱线图
        
        Args:
            data: 图表数据
            column: 要绘制箱线图的列名或列名列表
            by: 分组列名
            **kwargs: 传递给BaseChart的其他参数
        """
        super().__init__(data, **kwargs)
        self.column = column
        self.by = by
        self.chart_type = ChartType.BOX
        
    def plot(self):
        """绘制箱线图
        
        Returns:
            Figure: matplotlib图形对象
        """
        if self.figure is None:
            self.create_figure()
            
        if isinstance(self.data, pd.DataFrame):
            if self.column is not None:
                if self.by is not None:
                    self.data.boxplot(column=self.column, by=self.by, ax=self.axes)
                else:
                    self.data.boxplot(column=self.column, ax=self.axes)
            else:
                self.data.boxplot(ax=self.axes)
        elif isinstance(self.data, (list, np.ndarray)):
            self.axes.boxplot(self.data)
            
        self.set_title(self.title)
        self.set_labels(self.x_label, self.y_label)
        self.figure.tight_layout()
        return self.figure


class HeatmapChart(BaseChart):
    """热图实现"""
    
    def __init__(self, data=None, cmap='viridis', annot=False, **kwargs):
        """初始化热图
        
        Args:
            data: 图表数据，通常是二维数组或DataFrame
            cmap: 颜色映射
            annot: 是否在每个单元格上显示数值
            **kwargs: 传递给BaseChart的其他参数
        """
        super().__init__(data, **kwargs)
        self.cmap = cmap
        self.annot = annot
        self.chart_type = ChartType.HEATMAP
        
    def plot(self):
        """绘制热图
        
        Returns:
            Figure: matplotlib图形对象
        """
        if self.figure is None:
            self.create_figure()
            
        # 热图需要seaborn库
        try:
            import seaborn as sns
            
            if isinstance(self.data, pd.DataFrame):
                sns.heatmap(
                    self.data, 
                    ax=self.axes, 
                    cmap=self.cmap,
                    annot=self.annot
                )
            elif isinstance(self.data, (list, np.ndarray)):
                sns.heatmap(
                    self.data, 
                    ax=self.axes, 
                    cmap=self.cmap,
                    annot=self.annot
                )
        except ImportError:
            # 如果没有seaborn，使用matplotlib的imshow
            if isinstance(self.data, pd.DataFrame):
                im = self.axes.imshow(self.data.values, cmap=self.cmap)
                if self.annot:
                    for i in range(len(self.data.index)):
                        for j in range(len(self.data.columns)):
                            self.axes.text(
                                j, i, 
                                f"{self.data.values[i, j]:.2f}", 
                                ha="center", va="center"
                            )
                self.axes.set_xticks(range(len(self.data.columns)))
                self.axes.set_yticks(range(len(self.data.index)))
                self.axes.set_xticklabels(self.data.columns)
                self.axes.set_yticklabels(self.data.index)
            elif isinstance(self.data, (list, np.ndarray)):
                im = self.axes.imshow(self.data, cmap=self.cmap)
                if self.annot:
                    for i in range(self.data.shape[0]):
                        for j in range(self.data.shape[1]):
                            self.axes.text(
                                j, i, 
                                f"{self.data[i, j]:.2f}", 
                                ha="center", va="center"
                            )
            
            self.figure.colorbar(im, ax=self.axes)
            
        self.set_title(self.title)
        self.figure.tight_layout()
        return self.figure