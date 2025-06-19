"""分析模块基础类

定义分析结果和分析器的基础类。
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import pandas as pd
import numpy as np
import json
import uuid
from datetime import datetime

from scientific_analysis.models.dataset import Dataset
from scientific_analysis.visualization import BaseChart


class AnalysisResult:
    """分析结果类

    存储和管理分析操作的结果数据。
    """

    def __init__(self,
                 data: Optional[Union[pd.DataFrame, np.ndarray, Dict[str, Any]]] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 charts: Optional[List[BaseChart]] = None):
        """初始化分析结果

        Args:
            data: 分析结果数据，可以是DataFrame、NumPy数组或字典
            metadata: 结果元数据，包含分析类型、参数等信息
            charts: 与结果关联的图表列表
        """
        self.id = str(uuid.uuid4())
        self.timestamp = datetime.now()
        self.data = data
        self.metadata = metadata or {}
        self.charts = charts or []

        # 确保元数据包含基本信息
        if 'analysis_type' not in self.metadata:
            self.metadata['analysis_type'] = 'unknown'
        if 'timestamp' not in self.metadata:
            self.metadata['timestamp'] = self.timestamp.isoformat()
        if 'id' not in self.metadata:
            self.metadata['id'] = self.id

    def add_chart(self, chart: BaseChart) -> 'AnalysisResult':
        """添加图表到结果

        Args:
            chart: 要添加的图表对象

        Returns:
            AnalysisResult: 返回自身，支持链式调用
        """
        self.charts.append(chart)
        return self

    def get_data_as_dataframe(self) -> pd.DataFrame:
        """将结果数据转换为DataFrame

        Returns:
            pd.DataFrame: 结果数据的DataFrame表示

        Raises:
            ValueError: 如果数据无法转换为DataFrame
        """
        if self.data is None:
            return pd.DataFrame()

        if isinstance(self.data, pd.DataFrame):
            return self.data
        elif isinstance(self.data, np.ndarray):
            return pd.DataFrame(self.data)
        elif isinstance(self.data, dict):
            return pd.DataFrame(self.data)
        else:
            try:
                return pd.DataFrame(self.data)
            except Exception as e:
                raise ValueError(f"无法将数据转换为DataFrame: {str(e)}")

    def to_dict(self) -> Dict[str, Any]:
        """将分析结果转换为字典

        Returns:
            Dict[str, Any]: 结果的字典表示
        """
        result = {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'charts_count': len(self.charts)
        }

        # 尝试转换数据为可序列化格式
        if self.data is not None:
            if isinstance(self.data, pd.DataFrame):
                result['data'] = self.data.to_dict(orient='records')
            elif isinstance(self.data, np.ndarray):
                result['data'] = self.data.tolist()
            elif isinstance(self.data, dict):
                result['data'] = self.data
            else:
                result['data'] = str(self.data)

        return result

    def to_json(self) -> str:
        """将分析结果转换为JSON字符串

        Returns:
            str: 结果的JSON表示
        """
        return json.dumps(self.to_dict(), default=str)

    def __str__(self) -> str:
        """返回分析结果的字符串表示

        Returns:
            str: 结果的字符串表示
        """
        return f"AnalysisResult(id={self.id}, type={self.metadata.get('analysis_type')}, charts={len(self.charts)})"

    def __repr__(self) -> str:
        """返回分析结果的详细字符串表示

        Returns:
            str: 结果的详细字符串表示
        """
        return self.__str__()


class BaseAnalyzer:
    """分析器基类

    所有分析器的基类，提供通用功能和接口。
    """

    def __init__(self, dataset: Optional[Dataset] = None):
        """初始化分析器

        Args:
            dataset: 要分析的数据集，可选
        """
        self.dataset = dataset
        self.results = []
        self.parameters = {}

    def set_dataset(self, dataset: Dataset) -> 'BaseAnalyzer':
        """设置要分析的数据集

        Args:
            dataset: 数据集对象

        Returns:
            BaseAnalyzer: 返回自身，支持链式调用
        """
        self.dataset = dataset
        return self

    def set_parameters(self, **kwargs) -> 'BaseAnalyzer':
        """设置分析参数

        Args:
            **kwargs: 参数名和值

        Returns:
            BaseAnalyzer: 返回自身，支持链式调用
        """
        self.parameters.update(kwargs)
        return self

    def analyze(self, **kwargs) -> AnalysisResult:
        """执行分析

        这是一个抽象方法，子类必须实现。

        Args:
            **kwargs: 分析参数

        Returns:
            AnalysisResult: 分析结果

        Raises:
            NotImplementedError: 如果子类未实现此方法
        """
        raise NotImplementedError("子类必须实现analyze方法")

    def validate_dataset(self) -> bool:
        """验证数据集是否适合分析

        Returns:
            bool: 数据集是否有效

        Raises:
            ValueError: 如果数据集无效或未设置
        """
        if self.dataset is None:
            raise ValueError("未设置数据集")

        if not hasattr(self.dataset, 'data') or self.dataset.data is None:
            raise ValueError("数据集不包含数据")

        return True

    def get_last_result(self) -> Optional[AnalysisResult]:
        """获取最近的分析结果

        Returns:
            Optional[AnalysisResult]: 最近的分析结果，如果没有则返回None
        """
        if not self.results:
            return None

        return self.results[-1]

    def clear_results(self) -> 'BaseAnalyzer':
        """清除所有分析结果

        Returns:
            BaseAnalyzer: 返回自身，支持链式调用
        """
        self.results = []
        return self

    def _create_result(self,
                       data: Optional[Union[pd.DataFrame, np.ndarray, Dict[str, Any]]] = None,
                       metadata: Optional[Dict[str, Any]] = None,
                       charts: Optional[List[BaseChart]] = None) -> AnalysisResult:
        """创建分析结果对象

        Args:
            data: 分析结果数据
            metadata: 结果元数据
            charts: 与结果关联的图表列表

        Returns:
            AnalysisResult: 创建的分析结果对象
        """
        # 合并默认元数据和提供的元数据
        meta = {
            'analysis_type': self.__class__.__name__,
            'parameters': self.parameters.copy()
        }
        if metadata:
            meta.update(metadata)

        # 创建结果对象
        result = AnalysisResult(data=data, metadata=meta, charts=charts)

        # 添加到结果历史
        self.results.append(result)

        return result
