"""分析模块

提供各种数据分析功能，包括描述性统计、相关性分析、回归分析和聚类分析等。
"""

from .base import AnalysisResult, BaseAnalyzer
from .descriptive import DescriptiveAnalyzer
from .correlation import CorrelationAnalyzer
from .regression import RegressionAnalyzer, RegressionType
from .clustering import ClusteringAnalyzer, ClusteringMethod

__all__ = [
    'AnalysisResult',
    'BaseAnalyzer',
    'DescriptiveAnalyzer',
    'CorrelationAnalyzer',
    'RegressionAnalyzer',
    'RegressionType',
    'ClusteringAnalyzer',
    'ClusteringMethod'
]