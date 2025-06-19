"""描述性统计分析

提供数据的描述性统计分析功能，如均值、中位数、标准差等。
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import pandas as pd
import numpy as np
from enum import Enum, auto

from .base import BaseAnalyzer, AnalysisResult
from scientific_analysis.models.dataset import Dataset
from scientific_analysis.visualization import LineChart, BarChart, HistogramChart, BoxPlot
from .descriptive_outlier_detection import detect_outliers_iqr, detect_outliers_zscore, detect_outliers_isolation


class StatType(Enum):
    """统计类型枚举"""
    BASIC = auto()       # 基本统计（计数、均值、中位数等）
    DISTRIBUTION = auto() # 分布统计（分位数、偏度、峰度等）
    ALL = auto()         # 所有统计


class DescriptiveAnalyzer(BaseAnalyzer):
    """描述性统计分析器
    
    提供数据的描述性统计分析功能。
    """
    
    def __init__(self, dataset: Optional[Dataset] = None):
        """初始化描述性统计分析器
        
        Args:
            dataset: 要分析的数据集，可选
        """
        super().__init__(dataset)
        
    def analyze(self, 
                columns: Optional[List[str]] = None,
                variables: Optional[List[str]] = None,  # 兼容性参数
                stat_type: StatType = StatType.ALL,
                basic_stats: bool = True,
                distribution_stats: bool = True,
                outliers: bool = False,
                outlier_method: str = 'iqr',
                outlier_threshold: float = 1.5,
                frequency_table: bool = False,
                include_charts: bool = True,
                **kwargs) -> AnalysisResult:
        """执行描述性统计分析
        
        Args:
            columns: 要分析的列名列表，如果为None则分析所有数值列
            variables: 要分析的变量列表（与columns等效，用于兼容性）
            stat_type: 统计类型，可选BASIC、DISTRIBUTION或ALL
            basic_stats: 是否计算基本统计量
            distribution_stats: 是否计算分布统计量
            outliers: 是否进行异常值检测
            outlier_method: 异常值检测方法（'iqr', 'zscore', 'isolation'）
            outlier_threshold: 异常值检测阈值
            frequency_table: 是否生成频率表（适用于分类变量）
            include_charts: 是否包含可视化图表
            **kwargs: 其他参数
            
        Returns:
            AnalysisResult: 分析结果
            
        Raises:
            ValueError: 如果数据集无效或未设置
        """
        # 验证数据集
        self.validate_dataset()
        
        # 获取数据
        df = self.dataset.data
        
        # 处理兼容性参数
        if variables is not None:
            columns = variables
        
        # 如果未指定列，根据分析类型选择列
        if columns is None:
            if frequency_table:
                # 频率表分析：选择所有列
                columns = df.columns.tolist()
            else:
                # 其他分析：只选择数值列
                columns = df.select_dtypes(include=['number']).columns.tolist()
        else:
            # 验证列是否存在
            for col in columns:
                if col not in df.columns:
                    raise ValueError(f"列 '{col}' 不存在于数据集中")
        
        # 根据分析类型分离数值列和分类列
        numeric_cols = [col for col in columns if col in df.select_dtypes(include=['number']).columns]
        categorical_cols = [col for col in columns if col in df.select_dtypes(include=['object', 'category']).columns]
        
        # 检查是否有有效的列进行分析
        if not frequency_table and not numeric_cols:
            raise ValueError("未找到有效的数值列进行分析")
        if frequency_table and not categorical_cols and not numeric_cols:
            raise ValueError("未找到有效的列进行频率表分析")
        
        # 根据参数执行分析
        basic_stats_result = None
        dist_stats_result = None
        outliers_result = None
        frequency_table_result = None
        
        if basic_stats and numeric_cols and (stat_type == StatType.BASIC or stat_type == StatType.ALL):
            basic_stats_result = self._calculate_basic_stats(df[numeric_cols])
            
        if distribution_stats and numeric_cols and (stat_type == StatType.DISTRIBUTION or stat_type == StatType.ALL):
            dist_stats_result = self._calculate_distribution_stats(df[numeric_cols])
            
        if outliers and numeric_cols:
            outliers_result = self._detect_outliers(df[numeric_cols], outlier_method, outlier_threshold)
            
        if frequency_table:
            # 对分类列和数值列都可以生成频率表
            freq_columns = categorical_cols + numeric_cols
            if freq_columns:
                frequency_table_result = self._calculate_frequency_table(df[freq_columns])
            
        # 计算缺失值信息
        missing_values_result = self._calculate_missing_values(df[columns])
            
        # 合并结果
        stats = {}
        if basic_stats_result is not None:
            stats.update(basic_stats_result)
        if dist_stats_result is not None:
            stats.update(dist_stats_result)
            
        # 创建结果数据
        result_data = {}
        if stats:
            result_data.update(stats)
        if outliers_result is not None:
            result_data['outliers'] = outliers_result
        if missing_values_result is not None:
            result_data['missing_values'] = missing_values_result
        if frequency_table_result is not None:
            result_data['frequency_table'] = frequency_table_result
        
        # 创建元数据
        metadata = {
            'analysis_type': 'descriptive',
            'columns': columns,
            'stat_type': stat_type.name
        }
        
        # 创建图表
        if include_charts:
            charts = self._create_charts(df[columns])
            # 将图表按类型分组添加到结果数据中
            chart_data = {'histogram': [], 'boxplot': [], 'barplot': []}
            for chart in charts:
                if hasattr(chart, '__class__'):
                    chart_type = chart.__class__.__name__.lower()
                    if 'histogram' in chart_type:
                        chart_data['histogram'].append(chart)
                    elif 'box' in chart_type:
                        chart_data['boxplot'].append(chart)
                    elif 'bar' in chart_type:
                        chart_data['barplot'].append(chart)
            result_data['charts'] = chart_data
            
        # 创建并返回结果
        return self._create_result(
            data=result_data,
            metadata=metadata,
            charts=[]
        )
        
    def _calculate_basic_stats(self, data: pd.DataFrame) -> Dict[str, Dict[str, Dict[str, float]]]:
        """计算基本统计量
        
        Args:
            data: 要分析的数据
            
        Returns:
            Dict[str, Dict[str, Dict[str, float]]]: 基本统计结果
        """
        basic_stats = {}
        
        for col in data.columns:
            col_data = data[col].dropna()
            if len(col_data) == 0:
                continue
                
            col_stats = {
                'count': data[col].count(),
                'mean': col_data.mean(),
                'std': col_data.std(),
                'min': col_data.min(),
                'max': col_data.max(),
                'median': col_data.median(),
                'sum': col_data.sum(),
                'variance': col_data.var()
            }
            
            basic_stats[col] = col_stats
        
        return {'basic_stats': basic_stats}
        
    def _calculate_distribution_stats(self, data: pd.DataFrame) -> Dict[str, Dict[str, Dict[str, float]]]:
        """计算分布统计量
        
        Args:
            data: 要分析的数据
            
        Returns:
            Dict[str, Dict[str, Dict[str, float]]]: 分布统计结果
        """
        from scipy import stats as scipy_stats
        
        distribution_stats = {}
        
        for col in data.columns:
            col_data = data[col].dropna()
            if len(col_data) == 0:
                continue
                
            col_stats = {}
            
            # 计算偏度和峰度
            col_stats['skewness'] = col_data.skew()
            col_stats['kurtosis'] = col_data.kurtosis()
            
            # 计算分位数
            col_stats['quantile_25'] = col_data.quantile(0.25)
            col_stats['quantile_50'] = col_data.quantile(0.5)
            col_stats['quantile_75'] = col_data.quantile(0.75)
            
            # 计算四分位距
            col_stats['iqr'] = col_stats['quantile_75'] - col_stats['quantile_25']
            
            # 正态性检验 (Shapiro-Wilk test)
            if len(col_data) >= 3:
                try:
                    statistic, p_value = scipy_stats.shapiro(col_data)
                    col_stats['normality_test'] = {
                        'statistic': statistic,
                        'p_value': p_value
                    }
                except:
                    col_stats['normality_test'] = {
                        'statistic': None,
                        'p_value': None
                    }
            
            distribution_stats[col] = col_stats
        
        return {'distribution_stats': distribution_stats}
        
    def _create_charts(self, data: pd.DataFrame) -> List[Any]:
        """创建描述性统计图表
        
        Args:
            data: 要可视化的数据
            
        Returns:
            List[Any]: 图表对象列表
        """
        charts = []
        
        # 分离数值列和分类列
        numeric_cols = data.select_dtypes(include=['number']).columns
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns
        
        # 为数值列创建直方图和箱线图
        for column in numeric_cols:
            # 直方图
            hist_chart = HistogramChart(data=data, column=column, title=f"{column} 分布直方图")
            hist_chart.set_labels(x_label=column, y_label="频率")
            charts.append(hist_chart)
            
            # 箱线图
            box_chart = BoxPlot(data=data, column=column, title=f"{column} 箱线图")
            charts.append(box_chart)
        
        # 为分类列创建条形图
        for column in categorical_cols:
            # 这里需要导入BarChart类
            from scientific_analysis.visualization.charts import BarChart
            # 计算频率数据
            value_counts = data[column].value_counts()
            bar_chart = BarChart(data=value_counts.to_frame().reset_index(), 
                               x='index', y=column, title=f"{column} 频率条形图")
            charts.append(bar_chart)
            
        return charts
    
    def _detect_outliers(self, data: pd.DataFrame, method: str = 'iqr', threshold: float = 1.5) -> Dict[str, Any]:
        """检测异常值
        
        Args:
            data: 要检测的数据
            method: 检测方法 ('iqr', 'zscore', 'isolation')
            threshold: 检测阈值
            
        Returns:
            Dict[str, Any]: 异常值检测结果
        """
        if method == 'iqr':
            return detect_outliers_iqr(data, threshold)
        elif method == 'zscore':
            return detect_outliers_zscore(data, threshold)
        elif method == 'isolation':
            return detect_outliers_isolation(data, threshold)
        else:
            raise ValueError(f"不支持的异常值检测方法: {method}")
        
    def summary(self, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """生成数据摘要
        
        Args:
            columns: 要包含在摘要中的列，如果为None则包含所有数值列
            
        Returns:
            pd.DataFrame: 摘要数据框
        """
        # 验证数据集
        self.validate_dataset()
        
        # 获取数据
        df = self.dataset.data
        
        # 如果未指定列，使用所有数值列
        if columns is None:
            columns = df.select_dtypes(include=['number']).columns.tolist()
        else:
            # 验证列是否存在
            for col in columns:
                if col not in df.columns:
                    raise ValueError(f"列 '{col}' 不存在于数据集中")
            
            # 只保留数值列
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            columns = [col for col in columns if col in numeric_cols]
            
            if not columns:
                raise ValueError("未找到有效的数值列进行分析")
                
        # 生成摘要
        return df[columns].describe()
        
    def frequency_table(self, column: str, bins: Optional[int] = None) -> pd.DataFrame:
        """生成频率表
        
        Args:
            column: 要分析的列名
            bins: 分箱数量，仅对数值列有效
            
        Returns:
            pd.DataFrame: 频率表
        """
        # 验证数据集
        self.validate_dataset()
        
        # 获取数据
        df = self.dataset.data
        
        # 验证列是否存在
        if column not in df.columns:
            raise ValueError(f"列 '{column}' 不存在于数据集中")
            
        # 根据列类型生成频率表
        if pd.api.types.is_numeric_dtype(df[column]):
            # 数值列，使用分箱
            if bins is None:
                bins = min(10, len(df[column].unique()))
                
            # 创建分箱
            hist, bin_edges = np.histogram(df[column].dropna(), bins=bins)
            
            # 创建频率表
            freq_table = pd.DataFrame({
                'bin_start': bin_edges[:-1],
                'bin_end': bin_edges[1:],
                'frequency': hist,
                'percentage': hist / len(df) * 100
            })
            
            # 创建区间标签
            freq_table['bin'] = [f"{start:.2f} - {end:.2f}" 
                                for start, end in zip(bin_edges[:-1], bin_edges[1:])]
            
            return freq_table
        else:
            # 分类列，使用值计数
            value_counts = df[column].value_counts(dropna=False)
            freq_table = pd.DataFrame({
                'value': value_counts.index,
                'frequency': value_counts.values,
                'percentage': value_counts.values / len(df) * 100
            })
            
            return freq_table
        
    def detect_outliers(self, columns: Optional[List[str]] = None, 
                        method: str = 'iqr') -> pd.DataFrame:
        """检测异常值
        
        Args:
            columns: 要检测的列名列表，如果为None则检测所有数值列
            method: 检测方法，可选'iqr'（四分位距法）或'zscore'（Z分数法）
            
        Returns:
            pd.DataFrame: 包含异常值的数据框
        """
        # 验证数据集
        self.validate_dataset()
        
        # 获取数据
        df = self.dataset.data
        
        # 如果未指定列，使用所有数值列
        if columns is None:
            columns = df.select_dtypes(include=['number']).columns.tolist()
        else:
            # 验证列是否存在
            for col in columns:
                if col not in df.columns:
                    raise ValueError(f"列 '{col}' 不存在于数据集中")
            
            # 只保留数值列
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            columns = [col for col in columns if col in numeric_cols]
            
            if not columns:
                raise ValueError("未找到有效的数值列进行分析")
                
        # 创建掩码
        mask = pd.DataFrame(False, index=df.index, columns=columns)
        
        # 根据方法检测异常值
        if method.lower() == 'iqr':
            # 四分位距法
            for col in columns:
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                mask[col] = (df[col] < lower_bound) | (df[col] > upper_bound)
        elif method.lower() == 'zscore':
            # Z分数法
            for col in columns:
                mean = df[col].mean()
                std = df[col].std()
                z_scores = (df[col] - mean) / std
                mask[col] = abs(z_scores) > 3
        else:
            raise ValueError(f"不支持的方法: {method}，可选'iqr'或'zscore'")
            
        # 创建结果
        outliers = df[mask.any(axis=1)].copy()
        
        # 添加异常值标记
        for col in columns:
            outlier_col = f"{col}_is_outlier"
            outliers[outlier_col] = mask.loc[outliers.index, col]
            
        return outliers
    
    def _calculate_missing_values(self, data: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """计算缺失值信息
        
        Args:
            data: 要分析的数据
            
        Returns:
            Dict[str, Dict[str, float]]: 缺失值信息，包含每列的缺失值数量和百分比
        """
        missing_info = {}
        
        for col in data.columns:
            missing_count = data[col].isnull().sum()
            total_count = len(data)
            missing_percentage = (missing_count / total_count) * 100 if total_count > 0 else 0
            
            missing_info[col] = {
                'count': missing_count,
                'percentage': missing_percentage
            }
            
        return missing_info
    
    def _calculate_frequency_table(self, data: pd.DataFrame) -> Dict[str, Dict[str, Dict[str, float]]]:
        """计算频率表
        
        Args:
            data: 要分析的数据
            
        Returns:
            Dict[str, Dict[str, Dict[str, float]]]: 频率表信息，包含每列每个值的计数和百分比
        """
        frequency_tables = {}
        
        for col in data.columns:
            # 计算值计数
            value_counts = data[col].value_counts(dropna=False)
            total_count = len(data)
            
            col_freq_table = {}
            for value, count in value_counts.items():
                percentage = (count / total_count) * 100 if total_count > 0 else 0
                col_freq_table[str(value)] = {
                    'count': count,
                    'percentage': percentage
                }
            
            frequency_tables[col] = col_freq_table
            
        return frequency_tables