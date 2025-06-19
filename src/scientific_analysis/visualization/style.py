"""图表样式管理

提供图表样式自定义和主题管理功能。
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np


class ChartStyle:
    """图表样式管理类
    
    用于管理和应用图表样式，包括颜色、字体、网格等。
    """
    
    # 预定义的颜色主题
    COLOR_THEMES = {
        'default': {
            'colors': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                      '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
            'background': 'white',
            'text': 'black',
            'grid': '#cccccc'
        },
        'dark': {
            'colors': ['#8dd3c7', '#fdb462', '#bebada', '#fb8072', '#80b1d3', 
                      '#b3de69', '#fccde5', '#d9d9d9', '#bc80bd', '#ccebc5'],
            'background': '#333333',
            'text': 'white',
            'grid': '#555555'
        },
        'pastel': {
            'colors': ['#a1c9f4', '#ffb482', '#8de5a1', '#ff9f9b', '#d0bbff', 
                      '#debb9b', '#fab0e4', '#cfcfcf', '#fffea3', '#b9f2f0'],
            'background': '#f8f9fa',
            'text': '#333333',
            'grid': '#dddddd'
        },
        'scientific': {
            'colors': ['#0173b2', '#de8f05', '#029e73', '#d55e00', '#cc78bc', 
                      '#ca9161', '#fbafe4', '#949494', '#ece133', '#56b4e9'],
            'background': 'white',
            'text': 'black',
            'grid': '#e0e0e0'
        }
    }
    
    def __init__(self, theme='default'):
        """初始化图表样式
        
        Args:
            theme: 样式主题名称，可选值为'default', 'dark', 'pastel', 'scientific'
        """
        self.theme = theme
        self.color_theme = self.COLOR_THEMES.get(theme, self.COLOR_THEMES['default'])
        self.font_family = 'sans-serif'
        self.font_size = 12
        self.title_size = 14
        self.grid = True
        self.grid_style = '--'
        self.grid_alpha = 0.7
        self.background_color = self.color_theme['background']
        self.text_color = self.color_theme['text']
        self.figure_size = (8, 6)
        self.dpi = 100
        
    def set_theme(self, theme):
        """设置样式主题
        
        Args:
            theme: 样式主题名称
            
        Returns:
            ChartStyle: 返回自身，支持链式调用
        """
        if theme in self.COLOR_THEMES:
            self.theme = theme
            self.color_theme = self.COLOR_THEMES[theme]
            self.background_color = self.color_theme['background']
            self.text_color = self.color_theme['text']
        return self
        
    def set_font(self, family=None, size=None, title_size=None):
        """设置字体样式
        
        Args:
            family: 字体族
            size: 基本字体大小
            title_size: 标题字体大小
            
        Returns:
            ChartStyle: 返回自身，支持链式调用
        """
        if family is not None:
            self.font_family = family
        if size is not None:
            self.font_size = size
        if title_size is not None:
            self.title_size = title_size
        return self
        
    def set_grid(self, show=True, style='--', alpha=0.7):
        """设置网格样式
        
        Args:
            show: 是否显示网格
            style: 网格线样式
            alpha: 网格线透明度
            
        Returns:
            ChartStyle: 返回自身，支持链式调用
        """
        self.grid = show
        self.grid_style = style
        self.grid_alpha = alpha
        return self
        
    def set_figure_size(self, width=8, height=6, dpi=100):
        """设置图形大小和分辨率
        
        Args:
            width: 宽度（英寸）
            height: 高度（英寸）
            dpi: 分辨率（每英寸点数）
            
        Returns:
            ChartStyle: 返回自身，支持链式调用
        """
        self.figure_size = (width, height)
        self.dpi = dpi
        return self
        
    def apply_to_figure(self, figure, axes):
        """将样式应用到matplotlib图形
        
        Args:
            figure: matplotlib图形对象
            axes: matplotlib轴对象
            
        Returns:
            tuple: (figure, axes) - 应用样式后的图形和轴对象
        """
        # 设置字体属性
        plt.rcParams['font.family'] = self.font_family
        plt.rcParams['font.size'] = self.font_size
        
        # 设置标题字体大小
        if axes.get_title():
            axes.title.set_fontsize(self.title_size)
            axes.title.set_color(self.text_color)
        
        # 设置轴标签颜色
        axes.xaxis.label.set_color(self.text_color)
        axes.yaxis.label.set_color(self.text_color)
        
        # 设置刻度标签颜色
        axes.tick_params(axis='x', colors=self.text_color)
        axes.tick_params(axis='y', colors=self.text_color)
        
        # 设置网格
        if self.grid:
            axes.grid(
                True, 
                linestyle=self.grid_style, 
                alpha=self.grid_alpha,
                color=self.color_theme['grid']
            )
        else:
            axes.grid(False)
        
        # 设置背景颜色
        axes.set_facecolor(self.background_color)
        figure.patch.set_facecolor(self.background_color)
        
        # 设置颜色循环
        axes.set_prop_cycle('color', self.color_theme['colors'])
        
        # 设置脊柱颜色
        for spine in axes.spines.values():
            spine.set_color(self.text_color)
        
        return figure, axes
    
    def create_figure(self):
        """创建一个应用了当前样式的新图形
        
        Returns:
            tuple: (figure, axes) - 新创建的图形和轴对象
        """
        figure = plt.figure(figsize=self.figure_size, dpi=self.dpi)
        axes = figure.add_subplot(111)
        return self.apply_to_figure(figure, axes)


class StyleManager:
    """样式管理器
    
    管理多个样式主题，提供样式切换和自定义功能。
    """
    
    def __init__(self):
        """初始化样式管理器"""
        self.styles = {}
        self.current_style = None
        
        # 初始化预定义样式
        for theme in ChartStyle.COLOR_THEMES.keys():
            self.styles[theme] = ChartStyle(theme)
        
        # 设置默认样式
        self.current_style = self.styles['default']
    
    def get_style(self, name='default'):
        """获取指定名称的样式
        
        Args:
            name: 样式名称
            
        Returns:
            ChartStyle: 样式对象
        """
        return self.styles.get(name, self.current_style)
    
    def set_current_style(self, name):
        """设置当前样式
        
        Args:
            name: 样式名称
            
        Returns:
            StyleManager: 返回自身，支持链式调用
        """
        if name in self.styles:
            self.current_style = self.styles[name]
        return self
    
    def add_style(self, name, style):
        """添加新样式
        
        Args:
            name: 样式名称
            style: 样式对象
            
        Returns:
            StyleManager: 返回自身，支持链式调用
        """
        self.styles[name] = style
        return self
    
    def apply_to_figure(self, figure, axes, style_name=None):
        """将指定样式应用到图形
        
        Args:
            figure: matplotlib图形对象
            axes: matplotlib轴对象
            style_name: 样式名称，如果为None则使用当前样式
            
        Returns:
            tuple: (figure, axes) - 应用样式后的图形和轴对象
        """
        style = self.get_style(style_name) if style_name else self.current_style
        return style.apply_to_figure(figure, axes)


# 创建全局样式管理器实例
style_manager = StyleManager()