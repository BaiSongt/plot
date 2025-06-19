#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试描述性统计分析器模块。
"""

import unittest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scientific_analysis.models.dataset import Dataset
from scientific_analysis.analysis.descriptive import DescriptiveAnalyzer


class TestDescriptiveAnalyzer(unittest.TestCase):
    """描述性统计分析器的测试用例。"""
    
    def setUp(self):
        """设置测试数据。"""
        # 创建测试数据
        self.test_data = pd.DataFrame({
            'numeric1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'numeric2': [10.5, 20.1, 30.3, 40.2, 50.5, 60.6, 70.7, 80.8, 90.9, 100.1],
            'category': ['A', 'B', 'A', 'B', 'C', 'A', 'B', 'C', 'D', 'E'],
            'binary': [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
        })
        
        # 添加一些异常值
        self.test_data_with_outliers = self.test_data.copy()
        self.test_data_with_outliers.loc[10] = [100, 1000, 'F', 1]  # 添加异常值
        
        # 添加一些缺失值
        self.test_data_with_na = self.test_data.copy()
        self.test_data_with_na.loc[5, 'numeric1'] = np.nan
        self.test_data_with_na.loc[6, 'numeric2'] = np.nan
        
        # 创建数据集
        self.dataset = Dataset(data=self.test_data, name="测试数据集")
        self.dataset_with_outliers = Dataset(data=self.test_data_with_outliers, name="带异常值的测试数据集")
        self.dataset_with_na = Dataset(data=self.test_data_with_na, name="带缺失值的测试数据集")
        
        # 创建分析器
        self.analyzer = DescriptiveAnalyzer(self.dataset)
        self.analyzer_with_outliers = DescriptiveAnalyzer(self.dataset_with_outliers)
        self.analyzer_with_na = DescriptiveAnalyzer(self.dataset_with_na)
    
    def tearDown(self):
        """清理测试资源。"""
        plt.close('all')  # 关闭所有图表窗口
    
    def test_basic_stats(self):
        """测试基本统计量计算。"""
        # 计算基本统计量
        result = self.analyzer.analyze(
            variables=['numeric1', 'numeric2'],
            basic_stats=True,
            distribution_stats=False,
            outliers=False,
            include_charts=False
        )
        
        # 验证结果是否包含基本统计量
        self.assertIn('basic_stats', result.data)
        basic_stats = result.data['basic_stats']
        
        # 验证统计量是否正确
        self.assertAlmostEqual(basic_stats['numeric1']['mean'], 5.5)
        self.assertAlmostEqual(basic_stats['numeric1']['median'], 5.5)
        self.assertAlmostEqual(basic_stats['numeric1']['std'], 3.0276503540974917)
        self.assertEqual(basic_stats['numeric1']['min'], 1)
        self.assertEqual(basic_stats['numeric1']['max'], 10)
        
        self.assertAlmostEqual(basic_stats['numeric2']['mean'], 55.47)
        self.assertAlmostEqual(basic_stats['numeric2']['median'], 55.55)
        self.assertAlmostEqual(basic_stats['numeric2']['std'], 30.389583376179704)
        self.assertAlmostEqual(basic_stats['numeric2']['min'], 10.5)
        self.assertAlmostEqual(basic_stats['numeric2']['max'], 100.1)
    
    def test_distribution_stats(self):
        """测试分布统计量计算。"""
        # 计算分布统计量
        result = self.analyzer.analyze(
            variables=['numeric1', 'numeric2'],
            basic_stats=False,
            distribution_stats=True,
            outliers=False,
            include_charts=False
        )
        
        # 验证结果是否包含分布统计量
        self.assertIn('distribution_stats', result.data)
        dist_stats = result.data['distribution_stats']
        
        # 验证统计量是否正确
        self.assertAlmostEqual(dist_stats['numeric1']['skewness'], 0.0)
        self.assertAlmostEqual(dist_stats['numeric1']['kurtosis'], -1.2)
        
        # 验证正态性检验结果
        self.assertIn('normality_test', dist_stats['numeric1'])
        self.assertIn('p_value', dist_stats['numeric1']['normality_test'])
    
    def test_frequency_table(self):
        """测试频率表生成。"""
        # 生成频率表
        result = self.analyzer.analyze(
            variables=['category'],
            basic_stats=False,
            distribution_stats=False,
            frequency_table=True,
            outliers=False,
            include_charts=False
        )
        
        # 验证结果是否包含频率表
        self.assertIn('frequency_table', result.data)
        freq_table = result.data['frequency_table']['category']
        
        # 验证频率表是否正确
        self.assertEqual(freq_table['A']['count'], 3)
        self.assertEqual(freq_table['B']['count'], 3)
        self.assertEqual(freq_table['C']['count'], 2)
        self.assertEqual(freq_table['D']['count'], 1)
        self.assertEqual(freq_table['E']['count'], 1)
        
        # 验证百分比是否正确
        self.assertAlmostEqual(freq_table['A']['percentage'], 30.0)
        self.assertAlmostEqual(freq_table['B']['percentage'], 30.0)
        self.assertAlmostEqual(freq_table['C']['percentage'], 20.0)
        self.assertAlmostEqual(freq_table['D']['percentage'], 10.0)
        self.assertAlmostEqual(freq_table['E']['percentage'], 10.0)
    
    def test_outlier_detection(self):
        """测试异常值检测。"""
        # 检测异常值
        result = self.analyzer_with_outliers.analyze(
            variables=['numeric1', 'numeric2'],
            basic_stats=False,
            distribution_stats=False,
            outliers=True,
            outlier_method='zscore',
            outlier_threshold=3.0,
            include_charts=False
        )
        
        # 验证结果是否包含异常值信息
        self.assertIn('outliers', result.data)
        outliers = result.data['outliers']
        
        # 验证异常值检测结果是否正确
        self.assertTrue(outliers['numeric1']['is_outlier'].iloc[10])
        self.assertTrue(outliers['numeric2']['is_outlier'].iloc[10])
        self.assertEqual(outliers['numeric1']['outlier_indices'][0], 10)
        self.assertEqual(outliers['numeric2']['outlier_indices'][0], 10)
    
    def test_charts_generation(self):
        """测试图表生成。"""
        # 生成图表
        result = self.analyzer.analyze(
            variables=['numeric1', 'numeric2', 'category'],
            basic_stats=True,
            distribution_stats=True,
            outliers=True,
            include_charts=True
        )
        
        # 验证结果是否包含图表
        self.assertIn('charts', result.data)
        charts = result.data['charts']
        
        # 验证是否生成了直方图
        self.assertIn('histogram', charts)
        self.assertEqual(len(charts['histogram']), 2)  # 两个数值变量的直方图
        
        # 验证是否生成了箱线图
        self.assertIn('boxplot', charts)
        self.assertEqual(len(charts['boxplot']), 2)  # 两个数值变量的箱线图
        
        # 验证是否生成了条形图（针对分类变量）
        self.assertIn('barplot', charts)
        self.assertEqual(len(charts['barplot']), 1)  # 一个分类变量的条形图
    
    def test_missing_values_handling(self):
        """测试缺失值处理。"""
        # 分析带缺失值的数据
        result = self.analyzer_with_na.analyze(
            variables=['numeric1', 'numeric2'],
            basic_stats=True,
            distribution_stats=False,
            outliers=False,
            include_charts=False
        )
        
        # 验证结果是否包含缺失值信息
        self.assertIn('missing_values', result.data)
        missing = result.data['missing_values']
        
        # 验证缺失值信息是否正确
        self.assertEqual(missing['numeric1']['count'], 1)
        self.assertEqual(missing['numeric2']['count'], 1)
        self.assertAlmostEqual(missing['numeric1']['percentage'], 10.0)
        self.assertAlmostEqual(missing['numeric2']['percentage'], 10.0)


if __name__ == '__main__':
    unittest.main()