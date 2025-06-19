#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试可视化模块。
"""

import unittest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scientific_analysis.models.dataset import Dataset
from scientific_analysis.visualization.basic import BasicVisualizer
from scientific_analysis.visualization.advanced import AdvancedVisualizer
from scientific_analysis.visualization.interactive import InteractiveVisualizer


class TestBasicVisualizer(unittest.TestCase):
    """基础可视化器的测试用例。"""
    
    def setUp(self):
        """设置测试数据。"""
        # 创建测试数据
        np.random.seed(42)
        n = 100
        
        # 数值数据
        x = np.linspace(0, 10, n)
        y1 = np.sin(x) + np.random.normal(0, 0.1, n)
        y2 = np.cos(x) + np.random.normal(0, 0.1, n)
        
        # 分类数据
        categories = np.random.choice(['A', 'B', 'C', 'D'], size=n)
        values = np.random.normal(10, 2, n)
        
        # 创建DataFrame
        self.test_data = pd.DataFrame({
            'x': x,
            'y1': y1,
            'y2': y2,
            'category': categories,
            'values': values
        })
        
        # 创建数据集
        self.dataset = Dataset(data=self.test_data, name="可视化测试数据集")
        
        # 创建可视化器
        self.visualizer = BasicVisualizer(self.dataset)
    
    def tearDown(self):
        """清理测试资源。"""
        plt.close('all')  # 关闭所有图表窗口
    
    def test_line_chart(self):
        """测试折线图生成。"""
        # 生成折线图
        fig = self.visualizer.line_chart(
            x='x',
            y=['y1', 'y2'],
            title='测试折线图',
            xlabel='X轴',
            ylabel='Y轴',
            legend=True
        )
        
        # 验证图表是否生成
        self.assertIsNotNone(fig)
        
        # 验证图表类型
        self.assertEqual(type(fig).__name__, 'Figure')
        
        # 验证图表中的线条数量（应该有2条线）
        axes = fig.get_axes()[0]
        lines = axes.get_lines()
        self.assertEqual(len(lines), 2)
    
    def test_bar_chart(self):
        """测试柱状图生成。"""
        # 生成柱状图
        fig = self.visualizer.bar_chart(
            x='category',
            y='values',
            title='测试柱状图',
            xlabel='类别',
            ylabel='值',
            orientation='vertical'
        )
        
        # 验证图表是否生成
        self.assertIsNotNone(fig)
        
        # 验证图表类型
        self.assertEqual(type(fig).__name__, 'Figure')
        
        # 验证图表中的柱子数量（应该有4个柱子，对应4个类别）
        axes = fig.get_axes()[0]
        bars = axes.patches
        self.assertEqual(len(bars), 4)
    
    def test_scatter_plot(self):
        """测试散点图生成。"""
        # 生成散点图
        fig = self.visualizer.scatter_plot(
            x='x',
            y='y1',
            color='category',
            title='测试散点图',
            xlabel='X轴',
            ylabel='Y轴'
        )
        
        # 验证图表是否生成
        self.assertIsNotNone(fig)
        
        # 验证图表类型
        self.assertEqual(type(fig).__name__, 'Figure')
        
        # 验证图表中的散点集合
        axes = fig.get_axes()[0]
        collections = axes.collections
        self.assertGreaterEqual(len(collections), 1)
    
    def test_histogram(self):
        """测试直方图生成。"""
        # 生成直方图
        fig = self.visualizer.histogram(
            variable='values',
            bins=10,
            title='测试直方图',
            xlabel='值',
            ylabel='频率'
        )
        
        # 验证图表是否生成
        self.assertIsNotNone(fig)
        
        # 验证图表类型
        self.assertEqual(type(fig).__name__, 'Figure')
        
        # 验证图表中的直方图
        axes = fig.get_axes()[0]
        patches = axes.patches
        self.assertEqual(len(patches), 10)  # 应该有10个柱子（bins=10）
    
    def test_box_plot(self):
        """测试箱线图生成。"""
        # 生成箱线图
        fig = self.visualizer.box_plot(
            variables=['y1', 'y2'],
            title='测试箱线图',
            xlabel='变量',
            ylabel='值'
        )
        
        # 验证图表是否生成
        self.assertIsNotNone(fig)
        
        # 验证图表类型
        self.assertEqual(type(fig).__name__, 'Figure')
        
        # 验证图表中的箱线图数量（应该有2个箱线图）
        axes = fig.get_axes()[0]
        # 检查是否有两个变量的箱线图
        self.assertGreaterEqual(len(axes.lines), 10)  # 每个箱线图至少有5条线（中位线、上下四分位线等）
        self.assertEqual(len(axes.get_xticklabels()), 2)  # 应该有两个x轴标签


class TestAdvancedVisualizer(unittest.TestCase):
    """高级可视化器的测试用例。"""
    
    def setUp(self):
        """设置测试数据。"""
        # 创建测试数据
        np.random.seed(42)
        n = 100
        
        # 相关数据
        x1 = np.random.normal(0, 1, n)
        x2 = x1 * 0.8 + np.random.normal(0, 0.5, n)
        x3 = x1 * -0.6 + np.random.normal(0, 0.7, n)
        x4 = np.random.normal(0, 1, n)
        
        # 分类数据
        categories = np.random.choice(['A', 'B', 'C'], size=n)
        
        # 创建DataFrame
        self.test_data = pd.DataFrame({
            'x1': x1,
            'x2': x2,
            'x3': x3,
            'x4': x4,
            'category': categories
        })
        
        # 创建热图数据
        self.heatmap_data = np.random.rand(10, 10)
        
        # 创建数据集
        self.dataset = Dataset(data=self.test_data, name="高级可视化测试数据集")
        
        # 创建可视化器
        self.visualizer = AdvancedVisualizer(self.dataset)
    
    def tearDown(self):
        """清理测试资源。"""
        plt.close('all')  # 关闭所有图表窗口
    
    def test_heatmap(self):
        """测试热图生成。"""
        # 计算相关矩阵
        corr_matrix = self.test_data[['x1', 'x2', 'x3', 'x4']].corr()
        
        # 生成热图
        fig = self.visualizer.heatmap(
            data=corr_matrix,
            title='相关性热图',
            cmap='coolwarm',
            annot=True
        )
        
        # 验证图表是否生成
        self.assertIsNotNone(fig)
        
        # 验证图表类型
        self.assertEqual(type(fig).__name__, 'Figure')
        
        # 验证热图是否存在
        axes = fig.get_axes()[0]
        collections = axes.collections
        self.assertGreaterEqual(len(collections), 1)
    
    def test_pair_plot(self):
        """测试散点图矩阵生成。"""
        # 生成散点图矩阵
        fig = self.visualizer.pair_plot(
            variables=['x1', 'x2', 'x3'],
            hue='category'
        )
        
        # 验证图表是否生成
        self.assertIsNotNone(fig)
    
    def test_violin_plot(self):
        """测试小提琴图生成。"""
        # 生成小提琴图
        fig = self.visualizer.violin_plot(
            x='category',
            y='x1',
            title='测试小提琴图',
            xlabel='类别',
            ylabel='值'
        )
        
        # 验证图表是否生成
        self.assertIsNotNone(fig)
        
        # 验证图表类型
        self.assertEqual(type(fig).__name__, 'Figure')
        
        # 验证小提琴图是否存在
        axes = fig.get_axes()[0]
        collections = axes.collections
        self.assertGreaterEqual(len(collections), 3)  # 至少应该有3个小提琴（3个类别）
    
    def test_3d_scatter(self):
        """测试3D散点图生成。"""
        # 生成3D散点图
        fig = self.visualizer.scatter_3d(
            x='x1',
            y='x2',
            z='x3',
            color='category',
            title='测试3D散点图'
        )
        
        # 验证图表是否生成
        self.assertIsNotNone(fig)
        
        # 验证图表类型
        self.assertEqual(type(fig).__name__, 'Figure')
        
        # 验证是否为3D图表
        axes = fig.get_axes()[0]
        self.assertEqual(axes.name, '3d')


class TestInteractiveVisualizer(unittest.TestCase):
    """交互式可视化器的测试用例。"""
    
    def setUp(self):
        """设置测试数据。"""
        # 创建测试数据
        np.random.seed(42)
        n = 100
        
        # 数值数据
        x = np.linspace(0, 10, n)
        y1 = np.sin(x) + np.random.normal(0, 0.1, n)
        y2 = np.cos(x) + np.random.normal(0, 0.1, n)
        
        # 分类数据
        categories = np.random.choice(['A', 'B', 'C', 'D'], size=n)
        values = np.random.normal(10, 2, n)
        
        # 创建DataFrame
        self.test_data = pd.DataFrame({
            'x': x,
            'y1': y1,
            'y2': y2,
            'category': categories,
            'values': values
        })
        
        # 创建数据集
        self.dataset = Dataset(data=self.test_data, name="交互式可视化测试数据集")
        
        # 创建可视化器
        self.visualizer = InteractiveVisualizer(self.dataset)
    
    def test_interactive_line(self):
        """测试交互式折线图生成。"""
        # 生成交互式折线图
        fig = self.visualizer.interactive_line(
            x='x',
            y=['y1', 'y2'],
            title='交互式折线图',
            xlabel='X轴',
            ylabel='Y轴'
        )
        
        # 验证图表是否生成（可能返回plotly图表对象）
        self.assertIsNotNone(fig)
    
    def test_interactive_scatter(self):
        """测试交互式散点图生成。"""
        # 生成交互式散点图
        fig = self.visualizer.interactive_scatter(
            x='x',
            y='y1',
            color='category',
            title='交互式散点图',
            xlabel='X轴',
            ylabel='Y轴'
        )
        
        # 验证图表是否生成
        self.assertIsNotNone(fig)
    
    def test_interactive_bar(self):
        """测试交互式柱状图生成。"""
        # 生成交互式柱状图
        fig = self.visualizer.interactive_bar(
            x='category',
            y='values',
            title='交互式柱状图',
            xlabel='类别',
            ylabel='值'
        )
        
        # 验证图表是否生成
        self.assertIsNotNone(fig)


if __name__ == '__main__':
    unittest.main()