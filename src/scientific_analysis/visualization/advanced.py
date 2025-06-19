"""高级可视化模块

提供高级的数据可视化功能。
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Dict, Any, Optional, Union, Tuple
from .base import BaseChart, ChartType


class AdvancedVisualizer:
    """高级可视化器
    
    提供高级的数据可视化功能，如热图、散点图矩阵、小提琴图和3D散点图等。
    """
    
    def __init__(self, data=None):
        """初始化高级可视化器
        
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
        
    def heatmap(self, data=None, title="热图", cmap="viridis", annot=False, **kwargs):
        """绘制热图
        
        Args:
            data: 热图数据，如相关矩阵
            title: 图表标题
            cmap: 颜色映射
            annot: 是否在热图上显示数值
            **kwargs: 其他参数传递给seaborn.heatmap
            
        Returns:
            matplotlib的Figure对象
        """
        if data is None:
            if self.data is None:
                raise ValueError("没有提供数据来绘制热图")
            data = self.data
            
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(data, cmap=cmap, annot=annot, ax=ax, **kwargs)
        
        ax.set_title(title)
        fig.tight_layout()
        
        return fig
    
    def pair_plot(self, variables=None, hue=None, **kwargs):
        """绘制散点图矩阵
        
        Args:
            variables: 要绘制的变量列表
            hue: 用于分组的变量
            **kwargs: 其他参数传递给seaborn.pairplot
            
        Returns:
            seaborn的PairGrid对象
        """
        if self.data is None:
            raise ValueError("没有提供数据来绘制散点图矩阵")
            
        if variables is None:
            # 如果没有指定变量，使用所有数值列
            variables = self.data.select_dtypes(include=[np.number]).columns.tolist()
            
        g = sns.pairplot(self.data, vars=variables, hue=hue, **kwargs)
        g.fig.tight_layout()
        
        return g.fig
    
    def violin_plot(self, x=None, y=None, title="小提琴图", xlabel="X轴", ylabel="Y轴", **kwargs):
        """绘制小提琴图
        
        Args:
            x: X轴变量
            y: Y轴变量
            title: 图表标题
            xlabel: X轴标签
            ylabel: Y轴标签
            **kwargs: 其他参数传递给seaborn.violinplot
            
        Returns:
            matplotlib的Figure对象
        """
        if self.data is None:
            raise ValueError("没有提供数据来绘制小提琴图")
            
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.violinplot(x=x, y=y, data=self.data, ax=ax, **kwargs)
        
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        fig.tight_layout()
        
        return fig
    
    def scatter_3d(self, x=None, y=None, z=None, color=None, title="3D散点图", **kwargs):
        """绘制3D散点图
        
        Args:
            x: X轴变量
            y: Y轴变量
            z: Z轴变量
            color: 用于着色的变量
            title: 图表标题
            **kwargs: 其他参数传递给Axes3D.scatter
            
        Returns:
            matplotlib的Figure对象
        """
        if self.data is None:
            raise ValueError("没有提供数据来绘制3D散点图")
            
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        if color is not None:
            # 如果提供了color参数，根据类别着色
            categories = self.data[color].unique()
            for category in categories:
                subset = self.data[self.data[color] == category]
                ax.scatter(subset[x], subset[y], subset[z], label=category, **kwargs)
            ax.legend()
        else:
            ax.scatter(self.data[x], self.data[y], self.data[z], **kwargs)
        
        ax.set_title(title)
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.set_zlabel(z)
        fig.tight_layout()
        
        return fig