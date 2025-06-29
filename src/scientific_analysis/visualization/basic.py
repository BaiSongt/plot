"""基础可视化模块

提供基础的数据可视化功能。
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from .base import BaseChart, ChartType


class BasicVisualizer:
    """基础可视化器
    
    提供简单的数据可视化功能，如折线图、柱状图、散点图等。
    """
    
    def __init__(self, data=None):
        """初始化基础可视化器
        
        Args:
            data: 要可视化的数据，可以是Dataset对象、DataFrame或其他兼容格式
        """
        if hasattr(data, 'data'):
            # 如果是Dataset对象，获取其data属性
            self.data = data.data
        else:
            self.data = data
        
    def set_data(self, data):
        """设置要可视化的数据
        
        Args:
            data: 要可视化的数据
        """
        if hasattr(data, 'data'):
            # 如果是Dataset对象，获取其data属性
            self.data = data.data
        else:
            self.data = data
        
    def line_chart(self, x=None, y=None, title="折线图", xlabel="X轴", ylabel="Y轴", legend=True, **kwargs):
        """绘制折线图
        
        Args:
            x: X轴数据列名或数据
            y: Y轴数据列名或数据列表
            title: 图表标题
            xlabel: X轴标签
            ylabel: Y轴标签
            legend: 是否显示图例
            **kwargs: 其他参数传递给matplotlib
            
        Returns:
            matplotlib的Figure对象
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if self.data is None:
            raise ValueError("没有提供数据来绘制折线图")
            
        if isinstance(y, list):
            # 如果y是列表，绘制多条线
            for col in y:
                ax.plot(self.data[x], self.data[col], label=col, **kwargs)
            if legend:
                ax.legend()
        else:
            # 否则绘制单条线
            ax.plot(self.data[x], self.data[y], label=y if legend else None, **kwargs)
            if legend:
                ax.legend()
                
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True)
        
        return fig
        
    def bar_chart(self, x=None, y=None, title="柱状图", xlabel="X轴", ylabel="Y轴", orientation="vertical", **kwargs):
        """绘制柱状图
        
        Args:
            x: X轴数据列名或数据
            y: Y轴数据列名或数据
            title: 图表标题
            xlabel: X轴标签
            ylabel: Y轴标签
            orientation: 柱状图方向，可选值为"vertical"或"horizontal"
            **kwargs: 其他参数传递给matplotlib
            
        Returns:
            matplotlib的Figure对象
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if self.data is None:
            raise ValueError("没有提供数据来绘制柱状图")
            
        if orientation == "vertical":
            # 垂直柱状图
            if isinstance(self.data, pd.DataFrame):
                # 如果是DataFrame，使用分组统计
                counts = self.data.groupby(x)[y].mean()
                ax.bar(counts.index, counts.values, **kwargs)
            else:
                ax.bar(self.data[x], self.data[y], **kwargs)
        else:
            # 水平柱状图
            if isinstance(self.data, pd.DataFrame):
                # 如果是DataFrame，使用分组统计
                counts = self.data.groupby(x)[y].mean()
                ax.barh(counts.index, counts.values, **kwargs)
            else:
                ax.barh(self.data[x], self.data[y], **kwargs)
                
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True)
        
        return fig
        
    def scatter_plot(self, x=None, y=None, color=None, title="散点图", xlabel="X轴", ylabel="Y轴", **kwargs):
        """绘制散点图
        
        Args:
            x: X轴数据列名或数据
            y: Y轴数据列名或数据
            color: 用于着色的变量
            title: 图表标题
            xlabel: X轴标签
            ylabel: Y轴标签
            **kwargs: 其他参数传递给matplotlib
            
        Returns:
            matplotlib的Figure对象
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if self.data is None:
            raise ValueError("没有提供数据来绘制散点图")
            
        if color is not None:
            # 如果提供了color参数，根据类别着色
            categories = self.data[color].unique()
            for category in categories:
                subset = self.data[self.data[color] == category]
                ax.scatter(subset[x], subset[y], label=category, **kwargs)
            ax.legend()
        else:
            ax.scatter(self.data[x], self.data[y], **kwargs)
                
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True)
        
        return fig
        
    def histogram(self, variable=None, bins=10, title="直方图", xlabel="值", ylabel="频率", **kwargs):
        """绘制直方图
        
        Args:
            variable: 要绘制直方图的变量
            bins: 直方图的箱数
            title: 图表标题
            xlabel: X轴标签
            ylabel: Y轴标签
            **kwargs: 其他参数传递给matplotlib
            
        Returns:
            matplotlib的Figure对象
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if self.data is None:
            raise ValueError("没有提供数据来绘制直方图")
            
        ax.hist(self.data[variable], bins=bins, **kwargs)
                
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True)
        
        return fig
        
    def box_plot(self, variables=None, title="箱线图", xlabel="变量", ylabel="值", **kwargs):
        """绘制箱线图
        
        Args:
            variables: 要绘制箱线图的变量列表
            title: 图表标题
            xlabel: X轴标签
            ylabel: Y轴标签
            **kwargs: 其他参数传递给matplotlib
            
        Returns:
            matplotlib的Figure对象
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if self.data is None:
            raise ValueError("没有提供数据来绘制箱线图")
            
        if isinstance(self.data, pd.DataFrame):
            # 如果是DataFrame，绘制指定变量的箱线图
            data_to_plot = [self.data[var] for var in variables]
            ax.boxplot(data_to_plot, labels=variables, **kwargs)
        else:
            # 如果不是DataFrame，直接绘制
            ax.boxplot(self.data, **kwargs)
            
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True)
        
        return fig
        
    def pie_chart(self, values=None, labels=None, title="饼图", **kwargs):
        """绘制饼图
        
        Args:
            values: 各部分的值
            labels: 各部分的标签
            title: 图表标题
            **kwargs: 其他参数传递给matplotlib
            
        Returns:
            matplotlib的Figure对象
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if self.data is None:
            raise ValueError("没有提供数据来绘制饼图")
            
        if isinstance(self.data, pd.DataFrame) and values in self.data.columns:
            # 如果是DataFrame，使用分组统计
            if labels in self.data.columns:
                counts = self.data.groupby(labels)[values].sum()
                ax.pie(counts.values, labels=counts.index, autopct='%1.1f%%', **kwargs)
            else:
                ax.pie(self.data[values], **kwargs)
        else:
            ax.pie(values, labels=labels, autopct='%1.1f%%', **kwargs)
            
        ax.set_title(title)
        ax.axis('equal')  # 保证饼图是圆的
        
        return fig
        
    def save_figure(self, fig, filename, dpi=300, **kwargs):
        """保存图表到文件
        
        Args:
            fig: matplotlib的Figure对象
            filename: 文件名
            dpi: 分辨率
            **kwargs: 其他参数传递给matplotlib
            
        Returns:
            保存的文件路径
        """
        fig.savefig(filename, dpi=dpi, **kwargs)
        return filename
        
    def show_figure(self, fig):
        """显示图表
        
        Args:
            fig: matplotlib的Figure对象
        """
        plt.show()
        
    def close_figure(self, fig=None):
        """关闭图表
        
        Args:
            fig: matplotlib的Figure对象，如果为None则关闭所有图表
        """
        if fig is None:
            plt.close('all')
        else:
            plt.close(fig)
        """绘制柱状图
        
        Args:
            x: X轴数据列名或数据
            y: Y轴数据列名或数据
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            **kwargs: 其他参数传递给matplotlib
            
        Returns:
            matplotlib的Figure和Axes对象
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if self.data is not None:
            if isinstance(self.data, pd.DataFrame):
                if x is not None and y is not None:
                    self.data.plot(x=x, y=y, kind='bar', ax=ax, **kwargs)
                else:
                    self.data.plot(kind='bar', ax=ax, **kwargs)
            else:
                if x is not None and y is not None:
                    ax.bar(x, y, **kwargs)
                else:
                    ax.bar(range(len(self.data)), self.data, **kwargs)
        elif x is not None and y is not None:
            ax.bar(x, y, **kwargs)
        else:
            raise ValueError("没有提供足够的数据来绘制图表")
            
        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.grid(True)
        
        return fig, ax
    
    def plot_scatter(self, x=None, y=None, title="散点图", x_label="X轴", y_label="Y轴", **kwargs):
        """绘制散点图
        
        Args:
            x: X轴数据列名或数据
            y: Y轴数据列名或数据
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            **kwargs: 其他参数传递给matplotlib
            
        Returns:
            matplotlib的Figure和Axes对象
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if self.data is not None:
            if isinstance(self.data, pd.DataFrame):
                if x is not None and y is not None:
                    self.data.plot(x=x, y=y, kind='scatter', ax=ax, **kwargs)
                else:
                    self.data.plot(kind='scatter', ax=ax, **kwargs)
            else:
                if x is not None and y is not None:
                    ax.scatter(x, y, **kwargs)
                else:
                    raise ValueError("散点图需要X和Y数据")
        elif x is not None and y is not None:
            ax.scatter(x, y, **kwargs)
        else:
            raise ValueError("没有提供足够的数据来绘制图表")
            
        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.grid(True)
        
        return fig, ax
    
    def plot_histogram(self, column=None, bins=10, title="直方图", x_label="值", y_label="频率", **kwargs):
        """绘制直方图
        
        Args:
            column: 要绘制的列名或数据
            bins: 直方图的箱数
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            **kwargs: 其他参数传递给matplotlib
            
        Returns:
            matplotlib的Figure和Axes对象
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if self.data is not None:
            if isinstance(self.data, pd.DataFrame):
                if column is not None:
                    self.data[column].plot(kind='hist', bins=bins, ax=ax, **kwargs)
                else:
                    self.data.plot(kind='hist', bins=bins, ax=ax, **kwargs)
            else:
                ax.hist(self.data, bins=bins, **kwargs)
        elif column is not None:
            ax.hist(column, bins=bins, **kwargs)
        else:
            raise ValueError("没有提供足够的数据来绘制图表")
            
        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.grid(True)
        
        return fig, ax
    
    def save_figure(self, fig, filename, dpi=300, format='png'):
        """保存图表到文件
        
        Args:
            fig: matplotlib的Figure对象
            filename: 文件名
            dpi: 分辨率
            format: 文件格式
        """
        fig.savefig(filename, dpi=dpi, format=format, bbox_inches='tight')
        
    def show(self):
        """显示当前图表"""
        plt.show()