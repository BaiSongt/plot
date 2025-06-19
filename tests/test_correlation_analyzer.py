#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试相关性分析器模块。
"""

import unittest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scientific_analysis.models.dataset import Dataset
from scientific_analysis.analysis.correlation import CorrelationAnalyzer


class TestCorrelationAnalyzer(unittest.TestCase):
    """相关性分析器的测试用例。"""
    
    def setUp(self):
        """设置测试数据。"""
        # 创建具有明确相关性的测试数据
        np.random.seed(42)
        n = 100
        
        # 创建相关变量
        x1 = np.random.normal(0, 1, n)
        x2 = x1 * 0.8 + np.random.normal(0, 0.5, n)  # 与x1强相关
        x3 = x1 * -0.6 + np.random.normal(0, 0.7, n)  # 与x1负相关
        x4 = np.random.normal(0, 1, n)  # 与其他变量无相关
        
        # 创建DataFrame
        self.test_data = pd.DataFrame({
            'x1': x1,
            'x2': x2,
            'x3': x3,
            'x4': x4,
            'category': np.random.choice(['A', 'B', 'C'], size=n)
        })
        
        # 创建数据集
        self.dataset = Dataset(data=self.test_data, name="相关性测试数据集")
        
        # 创建分析器
        self.analyzer = CorrelationAnalyzer(self.dataset)
    
    def tearDown(self):
        """清理测试资源。"""
        plt.close('all')  # 关闭所有图表窗口
    
    def test_pearson_correlation(self):
        """测试皮尔逊相关系数计算。"""
        # 计算皮尔逊相关系数
        result = self.analyzer.analyze(
            variables=['x1', 'x2', 'x3', 'x4'],
            method='pearson',
            alpha=0.05,
            include_charts=False
        )
        
        # 验证结果是否包含相关系数矩阵
        self.assertIn('correlation_matrix', result.data)
        corr_matrix = result.data['correlation_matrix']
        
        # 验证相关系数是否在预期范围内
        self.assertGreater(corr_matrix.loc['x1', 'x2'], 0.7)  # x1和x2应该强正相关
        self.assertLess(corr_matrix.loc['x1', 'x3'], -0.5)  # x1和x3应该负相关
        self.assertAlmostEqual(corr_matrix.loc['x1', 'x1'], 1.0)  # 自相关应该为1
        
        # 验证p值矩阵
        self.assertIn('p_value_matrix', result.data)
        p_matrix = result.data['p_value_matrix']
        
        # x1和x2的相关性应该显著（p值小于0.05）
        self.assertLess(p_matrix.loc['x1', 'x2'], 0.05)
        # x1和x3的相关性应该显著（p值小于0.05）
        self.assertLess(p_matrix.loc['x1', 'x3'], 0.05)
    
    def test_spearman_correlation(self):
        """测试斯皮尔曼相关系数计算。"""
        # 计算斯皮尔曼相关系数
        result = self.analyzer.analyze(
            variables=['x1', 'x2', 'x3', 'x4'],
            method='spearman',
            alpha=0.05,
            include_charts=False
        )
        
        # 验证结果是否包含相关系数矩阵
        self.assertIn('correlation_matrix', result.data)
        corr_matrix = result.data['correlation_matrix']
        
        # 验证相关系数是否在预期范围内
        self.assertGreater(corr_matrix.loc['x1', 'x2'], 0.7)  # x1和x2应该强正相关
        self.assertLess(corr_matrix.loc['x1', 'x3'], -0.5)  # x1和x3应该负相关
    
    def test_kendall_correlation(self):
        """测试肯德尔相关系数计算。"""
        # 计算肯德尔相关系数
        result = self.analyzer.analyze(
            variables=['x1', 'x2', 'x3', 'x4'],
            method='kendall',
            alpha=0.05,
            include_charts=False
        )
        
        # 验证结果是否包含相关系数矩阵
        self.assertIn('correlation_matrix', result.data)
        corr_matrix = result.data['correlation_matrix']
        
        # 验证相关系数是否在预期范围内
        self.assertGreater(corr_matrix.loc['x1', 'x2'], 0.5)  # x1和x2应该正相关
        self.assertLess(corr_matrix.loc['x1', 'x3'], -0.3)  # x1和x3应该负相关
    
    def test_significant_correlations(self):
        """测试显著相关对的识别。"""
        # 计算相关系数并识别显著相关对
        result = self.analyzer.analyze(
            variables=['x1', 'x2', 'x3', 'x4'],
            method='pearson',
            alpha=0.05,
            include_charts=False
        )
        
        # 验证结果是否包含显著相关对
        self.assertIn('significant_correlations', result.data)
        sig_corrs = result.data['significant_correlations']
        
        # 验证是否正确识别了显著相关对
        # 至少应该有x1-x2和x1-x3这两对显著相关
        self.assertGreaterEqual(len(sig_corrs), 2)
        
        # 检查x1-x2是否在显著相关对中
        x1_x2_found = False
        for corr in sig_corrs:
            if (corr['var1'] == 'x1' and corr['var2'] == 'x2') or (corr['var1'] == 'x2' and corr['var2'] == 'x1'):
                x1_x2_found = True
                break
        self.assertTrue(x1_x2_found)
    
    def test_partial_correlation(self):
        """测试偏相关系数计算。"""
        # 计算偏相关系数
        result = self.analyzer.partial_correlation(
            variables=['x1', 'x2', 'x3'],
            control_variables=['x4']
        )
        
        # 验证结果是否包含偏相关系数矩阵
        self.assertIn('partial_correlation_matrix', result)
        partial_corr = result['partial_correlation_matrix']
        
        # 验证偏相关系数是否在预期范围内
        self.assertGreater(partial_corr.loc['x1', 'x2'], 0.7)  # 控制x4后，x1和x2仍应强相关
        self.assertLess(partial_corr.loc['x1', 'x3'], -0.5)  # 控制x4后，x1和x3仍应负相关
    
    def test_charts_generation(self):
        """测试图表生成。"""
        # 生成图表
        result = self.analyzer.analyze(
            variables=['x1', 'x2', 'x3', 'x4'],
            method='pearson',
            alpha=0.05,
            include_charts=True
        )
        
        # 验证结果是否包含图表
        self.assertIn('charts', result.data)
        charts = result.data['charts']
        
        # 验证是否生成了热图
        self.assertIn('heatmap', charts)
        self.assertIsNotNone(charts['heatmap'])
        
        # 验证是否生成了散点图矩阵
        self.assertIn('scatter_matrix', charts)
        self.assertIsNotNone(charts['scatter_matrix'])


if __name__ == '__main__':
    unittest.main()