#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
可视化和分析模块使用示例

本示例展示如何使用科学数据分析与可视化工具中的可视化和分析模块。
"""

import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入可视化模块
from src.scientific_analysis.visualization import (
    BaseChart, ChartType, LineChart, BarChart, ScatterChart,
    HistogramChart, PieChart, BoxPlot, HeatmapChart,
    InteractiveChart, ChartExporter
)

# 导入分析模块
from src.scientific_analysis.analysis import (
    AnalysisResult, BaseAnalyzer, DescriptiveAnalyzer,
    CorrelationAnalyzer, RegressionAnalyzer, RegressionType,
    ClusteringAnalyzer, ClusteringMethod
)

# 导入数据模型和管理器
from src.scientific_analysis.models.dataset import Dataset
from src.scientific_analysis.data.manager import DataManager


def create_sample_data():
    """创建示例数据"""
    # 创建一个包含多个特征的数据集
    np.random.seed(42)
    n_samples = 100
    
    # 创建特征
    x1 = np.random.normal(0, 1, n_samples)
    x2 = np.random.normal(2, 1.5, n_samples)
    x3 = np.random.uniform(-3, 3, n_samples)
    
    # 创建目标变量（线性关系加噪声）
    y = 2*x1 - 1.5*x2 + 0.5*x3 + np.random.normal(0, 1, n_samples)
    
    # 创建分类变量
    categories = np.random.choice(['A', 'B', 'C'], size=n_samples)
    
    # 创建DataFrame
    df = pd.DataFrame({
        'x1': x1,
        'x2': x2,
        'x3': x3,
        'y': y,
        'category': categories
    })
    
    # 创建数据集
    dataset = Dataset(
        data=df,
        name="示例数据集",
        description="用于演示可视化和分析功能的示例数据集"
    )
    
    return dataset


def visualization_examples(dataset):
    """可视化模块使用示例"""
    print("\n=== 可视化模块示例 ===")
    
    # 创建折线图
    print("\n创建折线图...")
    line_chart = LineChart()
    line_chart.set_data(dataset.data, x='x1', y='y')
    line_chart.set_title("x1 vs y 折线图")
    line_chart.set_labels(x_label="x1", y_label="y")
    line_chart.plot()
    
    # 创建柱状图
    print("\n创建柱状图...")
    bar_chart = BarChart()
    category_counts = dataset.data['category'].value_counts()
    bar_chart.set_data(category_counts.reset_index(), x='index', y='category')
    bar_chart.set_title("类别分布柱状图")
    bar_chart.set_labels(x_label="类别", y_label="计数")
    bar_chart.plot()
    
    # 创建散点图
    print("\n创建散点图...")
    scatter_chart = ScatterChart()
    scatter_chart.set_data(dataset.data, x='x1', y='x2', color='category')
    scatter_chart.set_title("x1 vs x2 散点图 (按类别着色)")
    scatter_chart.set_labels(x_label="x1", y_label="x2")
    scatter_chart.plot()
    
    # 创建直方图
    print("\n创建直方图...")
    hist_chart = HistogramChart()
    hist_chart.set_data(dataset.data, column='y')
    hist_chart.set_title("y 分布直方图")
    hist_chart.set_labels(x_label="y", y_label="频率")
    hist_chart.plot(bins=15)
    
    # 创建箱线图
    print("\n创建箱线图...")
    box_chart = BoxPlot()
    box_chart.set_data(dataset.data, column='x3', group_by='category')
    box_chart.set_title("x3 按类别分组的箱线图")
    box_chart.set_labels(x_label="类别", y_label="x3")
    box_chart.plot()
    
    # 创建热图
    print("\n创建热图...")
    heatmap_chart = HeatmapChart()
    corr_matrix = dataset.data.select_dtypes(include=['number']).corr()
    heatmap_chart.set_data(corr_matrix)
    heatmap_chart.set_title("相关性矩阵热图")
    heatmap_chart.plot(annot=True, cmap='coolwarm')
    
    # 创建交互式图表
    print("\n创建交互式图表...")
    interactive_chart = InteractiveChart()
    interactive_chart.set_data(dataset.data, x='x1', y='y')
    interactive_chart.set_title("交互式散点图")
    interactive_chart.set_labels(x_label="x1", y_label="y")
    interactive_chart.enable_zoom()
    interactive_chart.enable_hover()
    interactive_chart.plot()
    
    # 导出图表
    print("\n导出图表...")
    exporter = ChartExporter(scatter_chart)
    export_path = os.path.join(os.path.dirname(__file__), 'scatter_chart.png')
    exporter.export(export_path)
    print(f"图表已导出到: {export_path}")
    
    # 显示所有图表
    plt.show()


def analysis_examples(dataset):
    """分析模块使用示例"""
    print("\n=== 分析模块示例 ===")
    
    # 描述性统计分析
    print("\n执行描述性统计分析...")
    desc_analyzer = DescriptiveAnalyzer(dataset)
    desc_result = desc_analyzer.analyze(
        variables=['x1', 'x2', 'x3', 'y'],
        basic_stats=True,
        distribution_stats=True,
        outliers=True,
        include_charts=True
    )
    print("描述性统计结果:")
    print(desc_result.data)
    
    # 相关性分析
    print("\n执行相关性分析...")
    corr_analyzer = CorrelationAnalyzer(dataset)
    corr_result = corr_analyzer.analyze(
        variables=['x1', 'x2', 'x3', 'y'],
        method='pearson',
        alpha=0.05,
        include_charts=True
    )
    print("相关性分析结果:")
    print(corr_result.data)
    
    # 回归分析
    print("\n执行回归分析...")
    reg_analyzer = RegressionAnalyzer(dataset)
    reg_result = reg_analyzer.analyze(
        dependent_var='y',
        independent_vars=['x1', 'x2', 'x3'],
        regression_type=RegressionType.LINEAR,
        include_charts=True
    )
    print("回归分析结果:")
    print(reg_result.data)
    
    # 聚类分析
    print("\n执行聚类分析...")
    cluster_analyzer = ClusteringAnalyzer(dataset)
    cluster_result = cluster_analyzer.analyze(
        features=['x1', 'x2', 'x3'],
        method=ClusteringMethod.KMEANS,
        n_clusters=3,
        standardize=True,
        include_charts=True
    )
    print("聚类分析结果:")
    print(cluster_result.data)
    
    # 显示所有图表
    plt.show()


def data_manager_examples():
    """数据管理器使用示例"""
    print("\n=== 数据管理器示例 ===")
    
    # 创建数据管理器
    manager = DataManager()
    
    # 创建示例数据集
    dataset1 = create_sample_data()
    dataset1.name = "数据集1"
    
    # 添加数据集
    print("\n添加数据集...")
    dataset_id = manager.add_dataset(dataset1)
    print(f"数据集ID: {dataset_id}")
    
    # 获取数据集
    print("\n获取数据集...")
    retrieved_dataset = manager.get_dataset(dataset_id)
    print(f"获取的数据集: {retrieved_dataset}")
    
    # 创建并添加另一个数据集
    dataset2 = Dataset(
        data=pd.DataFrame({
            'A': np.random.rand(10),
            'B': np.random.rand(10)
        }),
        name="数据集2"
    )
    dataset2_id = manager.add_dataset(dataset2)
    
    # 获取所有数据集信息
    print("\n获取所有数据集信息...")
    all_datasets = manager.get_all_datasets_info()
    for ds_info in all_datasets:
        print(f"  - {ds_info['name']} (ID: {ds_info['id']}, 行数: {ds_info['rows']}, 列数: {ds_info['columns']})")
    
    # 获取当前数据集
    print("\n获取当前数据集...")
    current_dataset = manager.get_current_dataset()
    print(f"当前数据集: {current_dataset}")
    
    # 切换当前数据集
    print("\n切换当前数据集...")
    manager.set_current_dataset(dataset_id)
    current_dataset = manager.get_current_dataset()
    print(f"当前数据集: {current_dataset}")
    
    # 克隆数据集
    print("\n克隆数据集...")
    cloned_id = manager.clone_dataset(dataset_id, "克隆数据集")
    cloned_dataset = manager.get_dataset(cloned_id)
    print(f"克隆的数据集: {cloned_dataset}")
    
    # 移除数据集
    print("\n移除数据集...")
    removed = manager.remove_dataset(dataset2_id)
    print(f"数据集2已移除: {removed}")
    
    # 获取更新后的所有数据集信息
    print("\n更新后的所有数据集信息...")
    all_datasets = manager.get_all_datasets_info()
    for ds_info in all_datasets:
        print(f"  - {ds_info['name']} (ID: {ds_info['id']}, 行数: {ds_info['rows']}, 列数: {ds_info['columns']})")


def main():
    """主函数"""
    print("科学数据分析与可视化工具 - 示例程序")
    
    # 创建示例数据集
    dataset = create_sample_data()
    
    # 运行可视化示例
    visualization_examples(dataset)
    
    # 运行分析示例
    analysis_examples(dataset)
    
    # 运行数据管理器示例
    data_manager_examples()


if __name__ == "__main__":
    main()