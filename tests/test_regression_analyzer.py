#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试回归分析器模块。
"""

import unittest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scientific_analysis.models.dataset import Dataset
from scientific_analysis.analysis.regression import RegressionAnalyzer


class TestRegressionAnalyzer(unittest.TestCase):
    """回归分析器的测试用例。"""
    
    def setUp(self):
        """设置测试数据。"""
        # 创建具有明确关系的测试数据
        np.random.seed(42)
        n = 100
        
        # 线性关系数据
        x1 = np.random.uniform(0, 10, n)
        y1 = 2 * x1 + 3 + np.random.normal(0, 1, n)  # y = 2x + 3 + 噪声
        
        # 多元线性关系数据
        x2 = np.random.uniform(0, 5, n)
        x3 = np.random.uniform(-5, 5, n)
        y2 = 1.5 * x1 - 0.5 * x2 + 2 * x3 + 1 + np.random.normal(0, 1.5, n)
        
        # 逻辑回归数据
        x4 = np.random.uniform(-5, 5, n)
        x5 = np.random.uniform(-5, 5, n)
        z = 1.5 * x4 + 2 * x5
        prob = 1 / (1 + np.exp(-z))  # sigmoid函数
        y3 = np.random.binomial(1, prob)
        
        # 创建DataFrame
        self.test_data = pd.DataFrame({
            'x1': x1,
            'x2': x2,
            'x3': x3,
            'x4': x4,
            'x5': x5,
            'y1': y1,  # 简单线性回归目标
            'y2': y2,  # 多元线性回归目标
            'y3': y3,  # 逻辑回归目标（二分类）
            'category': np.random.choice(['A', 'B', 'C'], size=n)
        })
        
        # 创建数据集
        self.dataset = Dataset(data=self.test_data, name="回归测试数据集")
        
        # 创建分析器
        self.analyzer = RegressionAnalyzer(self.dataset)
    
    def tearDown(self):
        """清理测试资源。"""
        plt.close('all')  # 关闭所有图表窗口
    
    def test_simple_linear_regression(self):
        """测试简单线性回归。"""
        # 执行简单线性回归
        result = self.analyzer.linear_regression(
            dependent='y1',
            independents=['x1'],
            include_charts=False
        )
        
        # 验证结果是否包含模型摘要
        self.assertIn('model_summary', result)
        summary = result['model_summary']
        
        # 验证系数是否接近预期值
        self.assertIn('coefficients', result)
        coef = result['coefficients']
        self.assertAlmostEqual(coef['x1'], 2.0, delta=0.3)  # x1系数应接近2.0
        self.assertAlmostEqual(coef['intercept'], 3.0, delta=0.5)  # 截距应接近3.0
        
        # 验证R方是否合理
        self.assertIn('r_squared', result)
        r_squared = result['r_squared']
        self.assertGreater(r_squared, 0.8)  # R方应该很高
        
        # 验证p值是否显著
        self.assertIn('p_values', result)
        p_values = result['p_values']
        self.assertLess(p_values['x1'], 0.05)  # x1的p值应该显著
    
    def test_multiple_linear_regression(self):
        """测试多元线性回归。"""
        # 执行多元线性回归
        result = self.analyzer.linear_regression(
            dependent='y2',
            independents=['x1', 'x2', 'x3'],
            include_charts=False
        )
        
        # 验证结果是否包含模型摘要
        self.assertIn('model_summary', result)
        
        # 验证系数是否接近预期值
        self.assertIn('coefficients', result)
        coef = result['coefficients']
        self.assertAlmostEqual(coef['x1'], 1.5, delta=0.3)  # x1系数应接近1.5
        self.assertAlmostEqual(coef['x2'], -0.5, delta=0.3)  # x2系数应接近-0.5
        self.assertAlmostEqual(coef['x3'], 2.0, delta=0.3)  # x3系数应接近2.0
        self.assertAlmostEqual(coef['intercept'], 1.0, delta=0.5)  # 截距应接近1.0
        
        # 验证R方是否合理
        self.assertIn('r_squared', result)
        r_squared = result['r_squared']
        self.assertGreater(r_squared, 0.7)  # R方应该较高
        
        # 验证p值是否显著
        self.assertIn('p_values', result)
        p_values = result['p_values']
        self.assertLess(p_values['x1'], 0.05)  # x1的p值应该显著
        self.assertLess(p_values['x3'], 0.05)  # x3的p值应该显著
    
    def test_logistic_regression(self):
        """测试逻辑回归。"""
        # 执行逻辑回归
        result = self.analyzer.logistic_regression(
            dependent='y3',
            independents=['x4', 'x5'],
            include_charts=False
        )
        
        # 验证结果是否包含模型摘要
        self.assertIn('model_summary', result)
        
        # 验证系数是否接近预期值
        self.assertIn('coefficients', result)
        coef = result['coefficients']
        self.assertGreater(coef['x4'], 0)  # x4系数应为正
        self.assertGreater(coef['x5'], 0)  # x5系数应为正
        
        # 验证模型评估指标
        self.assertIn('accuracy', result)
        self.assertIn('precision', result)
        self.assertIn('recall', result)
        self.assertIn('f1_score', result)
        
        # 验证准确率是否合理
        accuracy = result['accuracy']
        self.assertGreater(accuracy, 0.7)  # 准确率应该较高
    
    def test_polynomial_regression(self):
        """测试多项式回归。"""
        # 创建具有非线性关系的数据
        n = 100
        x = np.linspace(-5, 5, n)
        y = 2 * x**2 - 3 * x + 1 + np.random.normal(0, 3, n)
        
        # 更新数据集
        self.test_data['x_poly'] = x
        self.test_data['y_poly'] = y
        self.dataset = Dataset(data=self.test_data, name="回归测试数据集")
        self.analyzer = RegressionAnalyzer(self.dataset)
        
        # 执行多项式回归
        result = self.analyzer.polynomial_regression(
            dependent='y_poly',
            independent='x_poly',
            degree=2,
            include_charts=False
        )
        
        # 验证结果是否包含模型摘要
        self.assertIn('model_summary', result)
        
        # 验证系数是否接近预期值
        self.assertIn('coefficients', result)
        coef = result['coefficients']
        
        # 验证R方是否合理
        self.assertIn('r_squared', result)
        r_squared = result['r_squared']
        self.assertGreater(r_squared, 0.7)  # R方应该较高
    
    def test_regression_prediction(self):
        """测试回归预测功能。"""
        # 训练线性回归模型
        self.analyzer.linear_regression(
            dependent='y1',
            independents=['x1'],
            include_charts=False
        )
        
        # 创建新数据进行预测
        new_data = pd.DataFrame({
            'x1': [2.5, 5.0, 7.5]
        })
        
        # 执行预测
        predictions = self.analyzer.predict(new_data)
        
        # 验证预测结果
        self.assertEqual(len(predictions), 3)  # 应该有3个预测值
        
        # 验证预测值是否在合理范围内
        # 对于x1=5.0，预期y1≈2*5.0+3=13.0
        expected_y1 = 2 * 5.0 + 3
        self.assertAlmostEqual(predictions[1], expected_y1, delta=2.0)
    
    def test_charts_generation(self):
        """测试图表生成。"""
        # 执行线性回归并生成图表
        result = self.analyzer.linear_regression(
            dependent='y1',
            independents=['x1'],
            include_charts=True
        )
        
        # 验证结果是否包含图表
        self.assertIn('charts', result)
        charts = result['charts']
        
        # 验证是否生成了散点图和回归线
        self.assertIn('scatter_plot', charts)
        self.assertIsNotNone(charts['scatter_plot'])
        
        # 验证是否生成了残差图
        self.assertIn('residual_plot', charts)
        self.assertIsNotNone(charts['residual_plot'])


if __name__ == '__main__':
    unittest.main()