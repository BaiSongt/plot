#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试聚类分析器模块。
"""

import unittest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scientific_analysis.models.dataset import Dataset
from scientific_analysis.analysis.clustering import ClusteringAnalyzer


class TestClusteringAnalyzer(unittest.TestCase):
    """聚类分析器的测试用例。"""
    
    def setUp(self):
        """设置测试数据。"""
        # 创建具有明确聚类结构的测试数据
        np.random.seed(42)
        
        # 创建三个明显的聚类
        n_per_cluster = 50
        
        # 第一个聚类
        cluster1_x = np.random.normal(0, 1, n_per_cluster)
        cluster1_y = np.random.normal(0, 1, n_per_cluster)
        
        # 第二个聚类
        cluster2_x = np.random.normal(8, 1, n_per_cluster)
        cluster2_y = np.random.normal(0, 1, n_per_cluster)
        
        # 第三个聚类
        cluster3_x = np.random.normal(4, 1, n_per_cluster)
        cluster3_y = np.random.normal(8, 1, n_per_cluster)
        
        # 合并数据
        x = np.concatenate([cluster1_x, cluster2_x, cluster3_x])
        y = np.concatenate([cluster1_y, cluster2_y, cluster3_y])
        
        # 添加一些额外的特征
        z = np.concatenate([
            np.random.normal(1, 0.5, n_per_cluster),
            np.random.normal(2, 0.5, n_per_cluster),
            np.random.normal(3, 0.5, n_per_cluster)
        ])
        
        # 真实的聚类标签（用于评估）
        true_labels = np.concatenate([
            np.zeros(n_per_cluster),
            np.ones(n_per_cluster),
            np.ones(n_per_cluster) * 2
        ]).astype(int)
        
        # 创建DataFrame
        self.test_data = pd.DataFrame({
            'x': x,
            'y': y,
            'z': z,
            'true_cluster': true_labels
        })
        
        # 创建数据集
        self.dataset = Dataset(data=self.test_data, name="聚类测试数据集")
        
        # 创建分析器
        self.analyzer = ClusteringAnalyzer(self.dataset)
    
    def tearDown(self):
        """清理测试资源。"""
        plt.close('all')  # 关闭所有图表窗口
    
    def test_kmeans_clustering(self):
        """测试K均值聚类。"""
        # 执行K均值聚类
        result = self.analyzer.kmeans_clustering(
            variables=['x', 'y'],
            n_clusters=3,
            include_charts=False
        )
        
        # 验证结果是否包含聚类标签
        self.assertIn('cluster_labels', result)
        labels = result['cluster_labels']
        
        # 验证标签数量是否正确
        self.assertEqual(len(labels), len(self.test_data))
        
        # 验证聚类数量是否为3
        self.assertEqual(len(np.unique(labels)), 3)
        
        # 验证聚类中心是否存在
        self.assertIn('cluster_centers', result)
        centers = result['cluster_centers']
        self.assertEqual(len(centers), 3)
        
        # 验证评估指标是否存在
        self.assertIn('silhouette_score', result)
        self.assertIn('inertia', result)
        
        # 验证轮廓系数是否合理（应该较高，因为聚类结构明显）
        silhouette = result['silhouette_score']
        self.assertGreater(silhouette, 0.5)
    
    def test_hierarchical_clustering(self):
        """测试层次聚类。"""
        # 执行层次聚类
        result = self.analyzer.hierarchical_clustering(
            variables=['x', 'y'],
            n_clusters=3,
            linkage='ward',
            include_charts=False
        )
        
        # 验证结果是否包含聚类标签
        self.assertIn('cluster_labels', result)
        labels = result['cluster_labels']
        
        # 验证标签数量是否正确
        self.assertEqual(len(labels), len(self.test_data))
        
        # 验证聚类数量是否为3
        self.assertEqual(len(np.unique(labels)), 3)
        
        # 验证评估指标是否存在
        self.assertIn('silhouette_score', result)
        
        # 验证轮廓系数是否合理
        silhouette = result['silhouette_score']
        self.assertGreater(silhouette, 0.5)
    
    def test_dbscan_clustering(self):
        """测试DBSCAN聚类。"""
        # 执行DBSCAN聚类
        result = self.analyzer.dbscan_clustering(
            variables=['x', 'y'],
            eps=2.0,  # 邻域半径
            min_samples=5,  # 最小样本数
            include_charts=False
        )
        
        # 验证结果是否包含聚类标签
        self.assertIn('cluster_labels', result)
        labels = result['cluster_labels']
        
        # 验证标签数量是否正确
        self.assertEqual(len(labels), len(self.test_data))
        
        # 验证是否识别出了主要聚类（可能会有噪声点标记为-1）
        unique_labels = np.unique(labels)
        n_clusters = len([l for l in unique_labels if l != -1])  # 排除噪声
        self.assertGreaterEqual(n_clusters, 2)  # 应该至少识别出2个聚类
        
        # 验证评估指标是否存在
        self.assertIn('silhouette_score', result)
        
        # 如果没有全部识别为噪声，验证轮廓系数
        if n_clusters > 0:
            silhouette = result['silhouette_score']
            self.assertGreater(silhouette, 0.3)  # DBSCAN的轮廓系数可能较低
    
    def test_optimal_k_selection(self):
        """测试最佳聚类数选择。"""
        # 执行最佳K值选择
        result = self.analyzer.find_optimal_clusters(
            variables=['x', 'y'],
            max_clusters=10,
            method='kmeans'
        )
        
        # 验证结果是否包含评估指标
        self.assertIn('silhouette_scores', result)
        self.assertIn('inertia_values', result)
        
        # 验证是否包含最佳聚类数
        self.assertIn('optimal_n_clusters', result)
        optimal_k = result['optimal_n_clusters']
        
        # 验证最佳聚类数是否合理（应该接近3）
        self.assertIn(optimal_k, [2, 3, 4])
        
        # 验证是否包含图表
        self.assertIn('elbow_plot', result)
        self.assertIn('silhouette_plot', result)
    
    def test_cluster_profiling(self):
        """测试聚类特征分析。"""
        # 先执行K均值聚类
        kmeans_result = self.analyzer.kmeans_clustering(
            variables=['x', 'y'],
            n_clusters=3,
            include_charts=False
        )
        
        # 获取聚类标签
        labels = kmeans_result['cluster_labels']
        
        # 执行聚类特征分析
        profile_result = self.analyzer.profile_clusters(
            cluster_labels=labels,
            variables=['x', 'y', 'z']
        )
        
        # 验证结果是否包含聚类统计信息
        self.assertIn('cluster_stats', profile_result)
        stats = profile_result['cluster_stats']
        
        # 验证是否包含每个聚类的统计信息
        for i in range(3):
            self.assertIn(i, stats)
            cluster_i_stats = stats[i]
            
            # 验证是否包含基本统计量
            self.assertIn('mean', cluster_i_stats)
            self.assertIn('std', cluster_i_stats)
            self.assertIn('min', cluster_i_stats)
            self.assertIn('max', cluster_i_stats)
            self.assertIn('count', cluster_i_stats)
        
        # 验证是否包含图表
        self.assertIn('profile_charts', profile_result)
    
    def test_charts_generation(self):
        """测试图表生成。"""
        # 执行K均值聚类并生成图表
        result = self.analyzer.kmeans_clustering(
            variables=['x', 'y'],
            n_clusters=3,
            include_charts=True
        )
        
        # 验证结果是否包含图表
        self.assertIn('charts', result)
        charts = result['charts']
        
        # 验证是否生成了散点图
        self.assertIn('scatter_plot', charts)
        self.assertIsNotNone(charts['scatter_plot'])
        
        # 验证是否生成了聚类中心图
        self.assertIn('cluster_centers_plot', charts)
        self.assertIsNotNone(charts['cluster_centers_plot'])


if __name__ == '__main__':
    unittest.main()