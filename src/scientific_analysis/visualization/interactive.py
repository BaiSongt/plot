"""交互式图表功能

提供图表交互功能，如缩放、平移、选择和注释等。
"""

from typing import Dict, List, Optional, Union, Any, Tuple, Callable
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider

from .base import BaseChart


class InteractiveChart(BaseChart):
    """交互式图表基类
    
    扩展基本图表类，添加交互功能。
    """
    
    def __init__(self, *args, **kwargs):
        """初始化交互式图表
        
        Args:
            *args: 传递给BaseChart的位置参数
            **kwargs: 传递给BaseChart的关键字参数
        """
        super().__init__(*args, **kwargs)
        self.selected_points = []
        self.annotations = []
        self.callbacks = {}
        self._interactive_enabled = False
        
    def enable_interactive(self):
        """启用交互功能
        
        Returns:
            InteractiveChart: 返回自身，支持链式调用
        """
        if self.figure is None:
            self.plot()
            
        self._interactive_enabled = True
        self.enable_zoom()
        self.enable_selection()
        return self
        
    def disable_interactive(self):
        """禁用交互功能
        
        Returns:
            InteractiveChart: 返回自身，支持链式调用
        """
        self._interactive_enabled = False
        return self
        
    def enable_zoom(self):
        """启用缩放功能
        
        Returns:
            InteractiveChart: 返回自身，支持链式调用
        """
        if self.figure is not None:
            self.figure.canvas.toolbar.zoom()
        return self
        
    def enable_pan(self):
        """启用平移功能
        
        Returns:
            InteractiveChart: 返回自身，支持链式调用
        """
        if self.figure is not None:
            self.figure.canvas.toolbar.pan()
        return self
        
    def enable_selection(self):
        """启用点选功能
        
        Returns:
            InteractiveChart: 返回自身，支持链式调用
        """
        # 实现点选功能的代码
        return self
        
    def add_annotation(self, x, y, text):
        """添加注释
        
        Args:
            x: X坐标
            y: Y坐标
            text: 注释文本
            
        Returns:
            InteractiveChart: 返回自身，支持链式调用
        """
        if self.axes is not None:
            annotation = self.axes.annotate(text, xy=(x, y), xytext=(10, 10),
                                          textcoords="offset points",
                                          arrowprops=dict(arrowstyle="->"))
            self.annotations.append(annotation)
        return self
        
    def clear_annotations(self):
        """清除所有注释
        
        Returns:
            InteractiveChart: 返回自身，支持链式调用
        """
        for annotation in self.annotations:
            annotation.remove()
        self.annotations = []
        return self
        
    def add_callback(self, event_type, callback):
        """添加事件回调函数
        
        Args:
            event_type: 事件类型
            callback: 回调函数
            
        Returns:
            InteractiveChart: 返回自身，支持链式调用
        """
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(callback)
        return self
        
    def remove_callback(self, event_type, callback):
        """移除事件回调函数
        
        Args:
            event_type: 事件类型
            callback: 回调函数
            
        Returns:
            InteractiveChart: 返回自身，支持链式调用
        """
        if event_type in self.callbacks and callback in self.callbacks[event_type]:
            self.callbacks[event_type].remove(callback)
        return self


class InteractiveVisualizer:
    """交互式可视化器
    
    提供交互式数据可视化功能，如交互式折线图、散点图和柱状图等。
    """
    
    def __init__(self, data=None):
        """初始化交互式可视化器
        
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
        
    def interactive_line(self, x=None, y=None, title="交互式折线图", xlabel="X轴", ylabel="Y轴", **kwargs):
        """绘制交互式折线图
        
        Args:
            x: X轴数据列名或数据
            y: Y轴数据列名或数据列表
            title: 图表标题
            xlabel: X轴标签
            ylabel: Y轴标签
            **kwargs: 其他参数传递给matplotlib
            
        Returns:
            matplotlib的Figure对象
        """
        if self.data is None:
            raise ValueError("没有提供数据来绘制交互式折线图")
            
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if isinstance(y, list):
            # 如果y是列表，绘制多条线
            for col in y:
                ax.plot(self.data[x], self.data[col], label=col, **kwargs)
            ax.legend()
        else:
            # 否则绘制单条线
            ax.plot(self.data[x], self.data[y], label=y, **kwargs)
            ax.legend()
            
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True)
        
        # 添加交互控件
        plt.subplots_adjust(bottom=0.25)
        ax_slider = plt.axes([0.25, 0.1, 0.65, 0.03])
        slider = Slider(ax_slider, '透明度', 0.1, 1.0, valinit=1.0)
        
        def update(val):
            for line in ax.get_lines():
                line.set_alpha(slider.val)
            fig.canvas.draw_idle()
            
        slider.on_changed(update)
        
        return fig
    
    def interactive_scatter(self, x=None, y=None, color=None, title="交互式散点图", xlabel="X轴", ylabel="Y轴", **kwargs):
        """绘制交互式散点图
        
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
        if self.data is None:
            raise ValueError("没有提供数据来绘制交互式散点图")
            
        fig, ax = plt.subplots(figsize=(10, 6))
        
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
        
        # 添加交互控件
        plt.subplots_adjust(bottom=0.25)
        ax_slider = plt.axes([0.25, 0.1, 0.65, 0.03])
        slider = Slider(ax_slider, '点大小', 10, 100, valinit=30)
        
        def update(val):
            for scatter in ax.collections:
                scatter.set_sizes([slider.val])
            fig.canvas.draw_idle()
            
        slider.on_changed(update)
        
        return fig
    
    def interactive_bar(self, x=None, y=None, title="交互式柱状图", xlabel="X轴", ylabel="Y轴", **kwargs):
        """绘制交互式柱状图
        
        Args:
            x: X轴数据列名或数据
            y: Y轴数据列名或数据
            title: 图表标题
            xlabel: X轴标签
            ylabel: Y轴标签
            **kwargs: 其他参数传递给matplotlib
            
        Returns:
            matplotlib的Figure对象
        """
        if self.data is None:
            raise ValueError("没有提供数据来绘制交互式柱状图")
            
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if isinstance(self.data, pd.DataFrame):
            # 如果是DataFrame，使用分组统计
            counts = self.data.groupby(x)[y].mean()
            ax.bar(counts.index, counts.values, **kwargs)
        else:
            ax.bar(self.data[x], self.data[y], **kwargs)
            
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True)
        
        # 添加交互控件
        plt.subplots_adjust(bottom=0.25)
        ax_slider = plt.axes([0.25, 0.1, 0.65, 0.03])
        slider = Slider(ax_slider, '柱宽', 0.1, 1.0, valinit=0.8)
        
        def update(val):
            for bar in ax.patches:
                bar.set_width(slider.val)
            fig.canvas.draw_idle()
            
        slider.on_changed(update)
        
        return fig