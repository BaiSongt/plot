"""相关性分析

提供变量之间相关性分析功能，包括相关系数计算、相关性矩阵和热图生成等。
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import pandas as pd
import numpy as np
from enum import Enum, auto
import scipy.stats as stats

from .base import BaseAnalyzer, AnalysisResult
from scientific_analysis.models.dataset import Dataset
from scientific_analysis.visualization import HeatmapChart, ScatterChart


class CorrelationMethod(Enum):
    """相关性计算方法枚举"""
    PEARSON = 'pearson'     # 皮尔逊相关系数
    SPEARMAN = 'spearman'   # 斯皮尔曼等级相关系数
    KENDALL = 'kendall'     # 肯德尔等级相关系数


class CorrelationAnalyzer(BaseAnalyzer):
    """相关性分析器
    
    提供变量之间相关性分析功能。
    """
    
    def __init__(self, dataset: Optional[Dataset] = None):
        """初始化相关性分析器
        
        Args:
            dataset: 要分析的数据集，可选
        """
        super().__init__(dataset)
        
    def analyze(self, 
                columns: Optional[List[str]] = None, 
                method: CorrelationMethod = CorrelationMethod.PEARSON,
                include_p_values: bool = True,
                include_charts: bool = True,
                **kwargs) -> AnalysisResult:
        """执行相关性分析
        
        Args:
            columns: 要分析的列名列表，如果为None则分析所有数值列
            method: 相关性计算方法
            include_p_values: 是否计算p值
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
                
        # 计算相关系数
        corr_matrix = self._calculate_correlation(df[columns], method.value)
        
        # 计算p值
        p_values = None
        if include_p_values:
            p_values = self._calculate_p_values(df[columns], method.value)
            
        # 创建结果数据
        result_data = {
            'correlation': corr_matrix
        }
        if p_values is not None:
            result_data['p_values'] = p_values
            
        # 创建元数据
        metadata = {
            'analysis_type': 'correlation',
            'method': method.value,
            'columns': columns,
            'include_p_values': include_p_values
        }
        
        # 创建图表
        charts = []
        if include_charts:
            charts = self._create_charts(corr_matrix, p_values)
            
        # 创建并返回结果
        return self._create_result(
            data=result_data,
            metadata=metadata,
            charts=charts
        )
        
    def _calculate_correlation(self, data: pd.DataFrame, method: str) -> pd.DataFrame:
        """计算相关系数矩阵
        
        Args:
            data: 要分析的数据
            method: 相关性计算方法
            
        Returns:
            pd.DataFrame: 相关系数矩阵
        """
        return data.corr(method=method)
        
    def _calculate_p_values(self, data: pd.DataFrame, method: str) -> pd.DataFrame:
        """计算相关系数的p值
        
        Args:
            data: 要分析的数据
            method: 相关性计算方法
            
        Returns:
            pd.DataFrame: p值矩阵
        """
        # 初始化p值矩阵
        p_values = pd.DataFrame(np.nan, index=data.columns, columns=data.columns)
        
        # 计算每对变量的p值
        for i, col1 in enumerate(data.columns):
            for j, col2 in enumerate(data.columns):
                if i == j:
                    p_values.loc[col1, col2] = 0.0
                    continue
                    
                # 去除缺失值
                valid_data = data[[col1, col2]].dropna()
                x = valid_data[col1]
                y = valid_data[col2]
                
                # 根据方法计算相关系数和p值
                if method == 'pearson':
                    corr, p = stats.pearsonr(x, y)
                elif method == 'spearman':
                    corr, p = stats.spearmanr(x, y)
                elif method == 'kendall':
                    corr, p = stats.kendalltau(x, y)
                else:
                    raise ValueError(f"不支持的方法: {method}")
                    
                p_values.loc[col1, col2] = p
                
        return p_values
        
    def _create_charts(self, corr_matrix: pd.DataFrame, 
                       p_values: Optional[pd.DataFrame] = None) -> List[Any]:
        """创建相关性分析图表
        
        Args:
            corr_matrix: 相关系数矩阵
            p_values: p值矩阵，可选
            
        Returns:
            List[Any]: 图表对象列表
        """
        charts = []
        
        # 创建热图
        heatmap = HeatmapChart(title="相关系数热图")
        heatmap.set_data(corr_matrix.values, 
                        x_labels=corr_matrix.columns.tolist(),
                        y_labels=corr_matrix.index.tolist())
        charts.append(heatmap)
        
        # 如果有p值，创建p值热图
        if p_values is not None:
            p_heatmap = HeatmapChart(title="相关系数p值热图")
            p_heatmap.set_data(p_values.values, 
                             x_labels=p_values.columns.tolist(),
                             y_labels=p_values.index.tolist())
            charts.append(p_heatmap)
            
        # 为每对变量创建散点图（最多10对）
        df = self.dataset.data
        columns = corr_matrix.columns.tolist()
        
        # 获取相关性最强的几对变量
        pairs = []
        for i in range(len(columns)):
            for j in range(i+1, len(columns)):
                col1, col2 = columns[i], columns[j]
                corr = abs(corr_matrix.loc[col1, col2])
                pairs.append((col1, col2, corr))
                
        # 按相关性强度排序并取前10对
        pairs.sort(key=lambda x: x[2], reverse=True)
        top_pairs = pairs[:min(10, len(pairs))]
        
        # 为每对创建散点图
        for col1, col2, corr in top_pairs:
            scatter = ScatterChart(title=f"{col1} vs {col2} (相关系数: {corr:.3f})")
            scatter.set_data(df[col1].values, df[col2].values)
            scatter.set_labels(x_label=col1, y_label=col2)
            charts.append(scatter)
            
        return charts
        
    def correlation_matrix(self, 
                          columns: Optional[List[str]] = None, 
                          method: CorrelationMethod = CorrelationMethod.PEARSON) -> pd.DataFrame:
        """计算相关系数矩阵
        
        Args:
            columns: 要分析的列名列表，如果为None则分析所有数值列
            method: 相关性计算方法
            
        Returns:
            pd.DataFrame: 相关系数矩阵
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
                
        # 计算相关系数
        return df[columns].corr(method=method.value)
        
    def significant_correlations(self, 
                               columns: Optional[List[str]] = None, 
                               method: CorrelationMethod = CorrelationMethod.PEARSON,
                               threshold: float = 0.5,
                               alpha: float = 0.05) -> pd.DataFrame:
        """获取显著相关的变量对
        
        Args:
            columns: 要分析的列名列表，如果为None则分析所有数值列
            method: 相关性计算方法
            threshold: 相关系数阈值，绝对值大于此值的相关系数被视为强相关
            alpha: 显著性水平，p值小于此值的相关系数被视为显著
            
        Returns:
            pd.DataFrame: 显著相关的变量对
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
                
        # 计算相关系数
        corr_matrix = df[columns].corr(method=method.value)
        
        # 计算p值
        p_values = self._calculate_p_values(df[columns], method.value)
        
        # 找出显著相关的变量对
        significant_pairs = []
        for i, col1 in enumerate(columns):
            for j, col2 in enumerate(columns):
                if i >= j:  # 只考虑上三角矩阵
                    continue
                    
                corr = corr_matrix.loc[col1, col2]
                p = p_values.loc[col1, col2]
                
                if abs(corr) >= threshold and p <= alpha:
                    significant_pairs.append({
                        'variable1': col1,
                        'variable2': col2,
                        'correlation': corr,
                        'p_value': p,
                        'significant': 'Yes'
                    })
                    
        # 创建结果数据框
        if significant_pairs:
            return pd.DataFrame(significant_pairs)
        else:
            return pd.DataFrame(columns=['variable1', 'variable2', 'correlation', 'p_value', 'significant'])
        
    def partial_correlation(self, 
                          var1: str, 
                          var2: str, 
                          control_vars: List[str]) -> Tuple[float, float]:
        """计算偏相关系数
        
        Args:
            var1: 第一个变量名
            var2: 第二个变量名
            control_vars: 控制变量列表
            
        Returns:
            Tuple[float, float]: 偏相关系数和p值
        """
        # 验证数据集
        self.validate_dataset()
        
        # 获取数据
        df = self.dataset.data
        
        # 验证列是否存在
        all_vars = [var1, var2] + control_vars
        for var in all_vars:
            if var not in df.columns:
                raise ValueError(f"列 '{var}' 不存在于数据集中")
                
        # 只保留数值列
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if not all(var in numeric_cols for var in all_vars):
            raise ValueError("所有变量必须是数值类型")
            
        # 去除缺失值
        data = df[all_vars].dropna()
        
        # 计算偏相关系数
        try:
            from pingouin import partial_corr
            
            result = partial_corr(data=data, x=var1, y=var2, covar=control_vars, method='pearson')
            r = result['r'].iloc[0]
            p = result['p-val'].iloc[0]
            
            return r, p
        except ImportError:
            # 如果没有pingouin库，使用statsmodels实现
            try:
                import statsmodels.api as sm
                
                # 为所有变量创建设计矩阵
                X = sm.add_constant(data[control_vars + [var1]])
                y = data[var2]
                
                # 拟合模型
                model = sm.OLS(y, X).fit()
                
                # 获取var1的系数和p值
                idx = control_vars.index(var1) + 1 if var1 in control_vars else len(control_vars) + 1
                r = model.params[idx]
                p = model.pvalues[idx]
                
                return r, p
            except ImportError:
                raise ImportError("计算偏相关系数需要pingouin或statsmodels库")
                
    def correlation_test(self, 
                        var1: str, 
                        var2: str, 
                        method: CorrelationMethod = CorrelationMethod.PEARSON) -> Dict[str, Any]:
        """执行相关性检验
        
        Args:
            var1: 第一个变量名
            var2: 第二个变量名
            method: 相关性计算方法
            
        Returns:
            Dict[str, Any]: 检验结果
        """
        # 验证数据集
        self.validate_dataset()
        
        # 获取数据
        df = self.dataset.data
        
        # 验证列是否存在
        for var in [var1, var2]:
            if var not in df.columns:
                raise ValueError(f"列 '{var}' 不存在于数据集中")
                
        # 只保留数值列
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if var1 not in numeric_cols or var2 not in numeric_cols:
            raise ValueError("变量必须是数值类型")
            
        # 去除缺失值
        valid_data = df[[var1, var2]].dropna()
        x = valid_data[var1]
        y = valid_data[var2]
        
        # 根据方法计算相关系数和p值
        if method == CorrelationMethod.PEARSON:
            corr, p = stats.pearsonr(x, y)
            method_name = "皮尔逊相关系数"
        elif method == CorrelationMethod.SPEARMAN:
            corr, p = stats.spearmanr(x, y)
            method_name = "斯皮尔曼等级相关系数"
        elif method == CorrelationMethod.KENDALL:
            corr, p = stats.kendalltau(x, y)
            method_name = "肯德尔等级相关系数"
        else:
            raise ValueError(f"不支持的方法: {method}")
            
        # 计算置信区间
        n = len(x)
        r_z = np.arctanh(corr)  # Fisher's Z变换
        se = 1 / np.sqrt(n - 3)
        z = stats.norm.ppf(0.975)  # 95%置信区间的Z值
        lo_z, hi_z = r_z - z * se, r_z + z * se
        lo, hi = np.tanh(lo_z), np.tanh(hi_z)  # 反变换回相关系数
        
        # 创建结果
        result = {
            'method': method_name,
            'variable1': var1,
            'variable2': var2,
            'correlation': corr,
            'p_value': p,
            'sample_size': n,
            'confidence_interval_95%': (lo, hi),
            'significant': p < 0.05
        }
        
        return result