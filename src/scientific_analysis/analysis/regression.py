"""回归分析

提供回归分析功能，包括线性回归、多项式回归、模型评估和诊断等。
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import pandas as pd
import numpy as np
from enum import Enum, auto
import scipy.stats as stats
import statsmodels.api as sm

from .base import BaseAnalyzer, AnalysisResult
from ..models.dataset import Dataset
from ..visualization import LineChart, ScatterChart


class RegressionType(Enum):
    """回归类型枚举"""
    LINEAR = auto()      # 线性回归
    POLYNOMIAL = auto()   # 多项式回归
    MULTIPLE = auto()     # 多元线性回归
    LOGISTIC = auto()    # 逻辑回归


class RegressionAnalyzer(BaseAnalyzer):
    """回归分析器
    
    提供回归分析功能。
    """
    
    def __init__(self, dataset: Optional[Dataset] = None):
        """初始化回归分析器
        
        Args:
            dataset: 要分析的数据集，可选
        """
        super().__init__(dataset)
        self.model = None
        self.model_params = {}
        
    def linear_regression(self, dependent: str, independents: List[str], include_charts: bool = True, **kwargs) -> Dict[str, Any]:
        """执行线性回归分析
        
        Args:
            dependent: 因变量（被预测变量）
            independents: 自变量（预测变量）列表
            include_charts: 是否包含可视化图表
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 回归分析结果
            
        Raises:
            ValueError: 如果数据集无效或未设置
        """
        regression_type = RegressionType.LINEAR if len(independents) == 1 else RegressionType.MULTIPLE
        result = self.analyze(
            dependent_var=dependent,
            independent_vars=independents,
            regression_type=regression_type,
            include_charts=include_charts,
            **kwargs
        )
        
        # 确保返回的是完整的数据字典
        if isinstance(result, AnalysisResult):
            result_dict = result.to_dict()
            # 提取data字段
            if 'data' in result_dict and isinstance(result_dict['data'], dict):
                data = result_dict['data']
            else:
                data = {}
                
            # 添加图表信息
            if include_charts and 'charts_count' in result_dict and result_dict['charts_count'] > 0:
                data['charts'] = result.charts
                
            return data
        else:
            # 如果result不是预期的AnalysisResult对象
            return {}
            
    def polynomial_regression(self, dependent: str, independent: str, degree: int = 2, include_charts: bool = True, **kwargs) -> Dict[str, Any]:
        """执行多项式回归分析
        
        Args:
            dependent: 因变量（被预测变量）
            independent: 自变量（预测变量）
            degree: 多项式阶数
            include_charts: 是否包含可视化图表
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 回归分析结果
            
        Raises:
            ValueError: 如果数据集无效或未设置
        """
        result = self.analyze(
            dependent_var=dependent,
            independent_vars=[independent],
            regression_type=RegressionType.POLYNOMIAL,
            polynomial_degree=degree,
            include_charts=include_charts,
            **kwargs
        )
        
        # 确保返回的是完整的数据字典
        if isinstance(result, AnalysisResult):
            result_dict = result.to_dict()
            # 提取data字段
            if 'data' in result_dict and isinstance(result_dict['data'], dict):
                data = result_dict['data']
            else:
                data = {}
                
            # 添加图表信息
            if include_charts and 'charts_count' in result_dict and result_dict['charts_count'] > 0:
                data['charts'] = result.charts
                
            return data
        else:
            # 如果result不是预期的AnalysisResult对象
            return {}
            
    def logistic_regression(self, dependent: str, independents: List[str], include_charts: bool = True, **kwargs) -> Dict[str, Any]:
        """执行逻辑回归分析
        
        Args:
            dependent: 因变量（被预测变量，二分类变量）
            independents: 自变量（预测变量）列表
            include_charts: 是否包含可视化图表
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 回归分析结果
            
        Raises:
            ValueError: 如果数据集无效或未设置
        """
        result = self.analyze(
            dependent_var=dependent,
            independent_vars=independents,
            regression_type=RegressionType.LOGISTIC,
            include_charts=include_charts,
            **kwargs
        )
        
        # 确保返回的是完整的数据字典
        if isinstance(result, AnalysisResult):
            result_dict = result.to_dict()
            # 提取data字段
            if 'data' in result_dict and isinstance(result_dict['data'], dict):
                data = result_dict['data']
            else:
                data = {}
                
            # 添加图表信息
            if include_charts and 'charts_count' in result_dict and result_dict['charts_count'] > 0:
                data['charts'] = result.charts
                
            return data
        else:
            # 如果result不是预期的AnalysisResult对象
            return {}
        
    def analyze(self, 
                dependent_var: str, 
                independent_vars: List[str],
                regression_type: RegressionType = RegressionType.LINEAR,
                polynomial_degree: int = 2,
                include_charts: bool = True,
                **kwargs) -> AnalysisResult:
        """执行回归分析
        
        Args:
            dependent_var: 因变量（被预测变量）
            independent_vars: 自变量（预测变量）列表
            regression_type: 回归类型
            polynomial_degree: 多项式回归的阶数
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
        
        # 验证列是否存在
        all_vars = [dependent_var] + independent_vars
        for var in all_vars:
            if var not in df.columns:
                raise ValueError(f"列 '{var}' 不存在于数据集中")
                
        # 只保留数值列
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if not all(var in numeric_cols for var in all_vars):
            raise ValueError("所有变量必须是数值类型")
            
        # 去除缺失值
        data = df[all_vars].dropna()
        
        # 根据回归类型执行分析
        if regression_type == RegressionType.LINEAR and len(independent_vars) == 1:
            # 简单线性回归
            result_data, model = self._linear_regression(data, dependent_var, independent_vars[0])
        elif regression_type == RegressionType.POLYNOMIAL and len(independent_vars) == 1:
            # 多项式回归
            result_data, model = self._polynomial_regression(data, dependent_var, independent_vars[0], polynomial_degree)
        elif regression_type == RegressionType.LOGISTIC:
            # 逻辑回归
            result_data, model = self._logistic_regression(data, dependent_var, independent_vars)
        elif regression_type == RegressionType.MULTIPLE or len(independent_vars) > 1:
            # 多元线性回归
            result_data, model = self._multiple_regression(data, dependent_var, independent_vars)
        else:
            raise ValueError(f"不支持的回归类型: {regression_type}")
            
        # 保存模型
        self.model = model
        self.model_params = {
            'dependent_var': dependent_var,
            'independent_vars': independent_vars,
            'regression_type': regression_type,
            'polynomial_degree': polynomial_degree
        }
        
        # 创建元数据
        metadata = {
            'analysis_type': 'regression',
            'regression_type': regression_type.name,
            'dependent_var': dependent_var,
            'independent_vars': independent_vars,
            'polynomial_degree': polynomial_degree if regression_type == RegressionType.POLYNOMIAL else None,
            'sample_size': len(data)
        }
        
        # 创建图表
        charts = []
        if include_charts:
            charts = self._create_charts(data, dependent_var, independent_vars, regression_type, polynomial_degree, model)
            
        # 创建并返回结果
        return self._create_result(
            data=result_data,
            metadata=metadata,
            charts=charts
        )
        
    def _linear_regression(self, data: pd.DataFrame, dependent_var: str, 
                          independent_var: str) -> Tuple[Dict[str, Any], Any]:
        """执行简单线性回归
        
        Args:
            data: 数据
            dependent_var: 因变量
            independent_var: 自变量
            
        Returns:
            Tuple[Dict[str, Any], Any]: 结果数据和模型
        """
        try:
            import statsmodels.api as sm
            from statsmodels.stats.outliers_influence import variance_inflation_factor
            
            # 准备数据
            X = data[independent_var].values.reshape(-1, 1)
            y = data[dependent_var].values
            
            # 添加常数项
            X_with_const = sm.add_constant(X)
            
            # 拟合模型
            model = sm.OLS(y, X_with_const).fit()
            
            # 获取结果
            params = model.params
            conf_int = model.conf_int()
            
            # 计算预测值和残差
            predictions = model.predict(X_with_const)
            residuals = y - predictions
            
            # 计算R方和调整R方
            r_squared = model.rsquared
            adj_r_squared = model.rsquared_adj
            
            # 计算F统计量和p值
            f_statistic = model.fvalue
            f_pvalue = model.f_pvalue
            
            # 计算标准误差
            std_errors = model.bse
            
            # 计算t统计量和p值
            t_values = model.tvalues
            p_values = model.pvalues
            
            # 计算AIC和BIC
            aic = model.aic
            bic = model.bic
            
            # 创建结果数据
            result_data = {
                'model_summary': model.summary().as_text(),
                'coefficients': {
                    'intercept': params[0],
                    independent_var: params[1]
                },
                'confidence_intervals': {
                    'intercept': (conf_int[0][0], conf_int[0][1]),
                    independent_var: (conf_int[1][0], conf_int[1][1])
                },
                'std_errors': {
                    'intercept': std_errors[0],
                    independent_var: std_errors[1]
                },
                't_values': {
                    'intercept': t_values[0],
                    independent_var: t_values[1]
                },
                'p_values': {
                    'intercept': p_values[0],
                    independent_var: p_values[1]
                },
                'r_squared': r_squared,
                'adj_r_squared': adj_r_squared,
                'f_statistic': f_statistic,
                'f_pvalue': f_pvalue,
                'aic': aic,
                'bic': bic,
                'equation': f"y = {params[0]:.4f} + {params[1]:.4f}x",
                'predictions': predictions.tolist(),
                'residuals': residuals.tolist()
            }
            
            return result_data, model
        except ImportError:
            # 如果没有statsmodels，使用scikit-learn
            from sklearn.linear_model import LinearRegression
            from sklearn.metrics import r2_score, mean_squared_error
            
            # 准备数据
            X = data[independent_var].values.reshape(-1, 1)
            y = data[dependent_var].values
            
            # 拟合模型
            model = LinearRegression()
            model.fit(X, y)
            
            # 获取结果
            intercept = model.intercept_
            slope = model.coef_[0]
            
            # 计算预测值和残差
            predictions = model.predict(X)
            residuals = y - predictions
            
            # 计算R方
            r_squared = r2_score(y, predictions)
            
            # 计算均方误差
            mse = mean_squared_error(y, predictions)
            
            # 计算p值（使用t检验）
            import numpy as np
            from scipy import stats
            
            n = len(X)  # 样本数量
            k = 1  # 自变量数量
            dof = n - k - 1  # 自由度
            
            # 计算标准误差
            residual_sum_of_squares = np.sum(residuals**2)
            sigma_squared = residual_sum_of_squares / dof
            
            # 计算X的均值
            x_mean = np.mean(X)
            
            # 计算标准误差
            se_slope = np.sqrt(sigma_squared / np.sum((X.flatten() - x_mean)**2))
            se_intercept = np.sqrt(sigma_squared * (1/n + x_mean**2 / np.sum((X.flatten() - x_mean)**2)))
            
            # 计算t值
            t_slope = slope / se_slope
            t_intercept = intercept / se_intercept
            
            # 计算p值
            p_slope = 2 * (1 - stats.t.cdf(abs(t_slope), dof))
            p_intercept = 2 * (1 - stats.t.cdf(abs(t_intercept), dof))
            
            # 创建结果数据
            result_data = {
                'model_summary': f"Linear Regression Results:\n\nDependent Variable: {dependent_var}\nIndependent Variable: {independent_var}\n\nIntercept: {intercept:.6f} (p={p_intercept:.6f})\nSlope: {slope:.6f} (p={p_slope:.6f})\n\nR-squared: {r_squared:.6f}\nMSE: {mse:.6f}",
                'coefficients': {
                    'intercept': intercept,
                    independent_var: slope
                },
                'r_squared': r_squared,
                'mse': mse,
                'equation': f"y = {intercept:.4f} + {slope:.4f}x",
                'predictions': predictions.tolist(),
                'residuals': residuals.tolist(),
                'p_values': {
                    'intercept': p_intercept,
                    independent_var: p_slope
                },
                'std_errors': {
                    'intercept': se_intercept,
                    independent_var: se_slope
                },
                't_values': {
                    'intercept': t_intercept,
                    independent_var: t_slope
                }
            }
            
            return result_data, model
            
    def _polynomial_regression(self, data: pd.DataFrame, dependent_var: str, 
                             independent_var: str, degree: int) -> Tuple[Dict[str, Any], Any]:
        """执行多项式回归
        
        Args:
            data: 数据
            dependent_var: 因变量
            independent_var: 自变量
            degree: 多项式阶数
            
        Returns:
            Tuple[Dict[str, Any], Any]: 结果数据和模型
        """
        try:
            import statsmodels.api as sm
            from sklearn.preprocessing import PolynomialFeatures
            
            # 准备数据
            X = data[independent_var].values.reshape(-1, 1)
            y = data[dependent_var].values
            
            # 创建多项式特征
            poly = PolynomialFeatures(degree=degree, include_bias=False)
            X_poly = poly.fit_transform(X)
            
            # 添加常数项
            X_with_const = sm.add_constant(X_poly)
            
            # 拟合模型
            model = sm.OLS(y, X_with_const).fit()
            
            # 获取结果
            params = model.params
            conf_int = model.conf_int()
            
            # 计算预测值和残差
            predictions = model.predict(X_with_const)
            residuals = y - predictions
            
            # 计算R方和调整R方
            r_squared = model.rsquared
            adj_r_squared = model.rsquared_adj
            
            # 计算F统计量和p值
            f_statistic = model.fvalue
            f_pvalue = model.f_pvalue
            
            # 计算AIC和BIC
            aic = model.aic
            bic = model.bic
            
            # 创建方程字符串
            equation = f"y = {params[0]:.4f}"
            for i in range(1, degree + 1):
                if params[i] >= 0:
                    equation += f" + {params[i]:.4f}x^{i}"
                else:
                    equation += f" - {abs(params[i]):.4f}x^{i}"
                    
            # 创建结果数据
            result_data = {
                'model_summary': model.summary().as_text(),
                'coefficients': {f"x^{i}": params[i] for i in range(degree + 1)},
                'r_squared': r_squared,
                'adj_r_squared': adj_r_squared,
                'f_statistic': f_statistic,
                'f_pvalue': f_pvalue,
                'aic': aic,
                'bic': bic,
                'equation': equation,
                'predictions': predictions.tolist(),
                'residuals': residuals.tolist(),
                'degree': degree
            }
            
            # 创建一个包含所有信息的模型对象
            model_info = {
                'model': model,
                'poly': poly,
                'degree': degree
            }
            
            return result_data, model_info
        except ImportError:
            # 如果没有statsmodels，使用scikit-learn
            from sklearn.preprocessing import PolynomialFeatures
            from sklearn.linear_model import LinearRegression
            from sklearn.pipeline import make_pipeline
            from sklearn.metrics import r2_score, mean_squared_error
            
            # 准备数据
            X = data[independent_var].values.reshape(-1, 1)
            y = data[dependent_var].values
            
            # 创建多项式回归模型
            model = make_pipeline(PolynomialFeatures(degree=degree), LinearRegression())
            model.fit(X, y)
            
            # 获取结果
            poly = model.named_steps['polynomialfeatures']
            lr = model.named_steps['linearregression']
            
            # 计算预测值和残差
            predictions = model.predict(X)
            residuals = y - predictions
            
            # 计算R方
            r_squared = r2_score(y, predictions)
            
            # 计算均方误差
            mse = mean_squared_error(y, predictions)
            
            # 创建方程字符串
            equation = f"y = {lr.intercept_:.4f}"
            for i, coef in enumerate(lr.coef_):
                if i == 0:
                    continue  # 跳过常数项
                if coef >= 0:
                    equation += f" + {coef:.4f}x^{i}"
                else:
                    equation += f" - {abs(coef):.4f}x^{i}"
                    
            # 创建结果数据
            result_data = {
                'coefficients': {f"x^{i}": coef for i, coef in enumerate(lr.coef_)},
                'intercept': lr.intercept_,
                'r_squared': r_squared,
                'mse': mse,
                'equation': equation,
                'predictions': predictions.tolist(),
                'residuals': residuals.tolist(),
                'degree': degree
            }
            
            return result_data, model
            
    def _multiple_regression(self, data: pd.DataFrame, dependent_var: str, 
                           independent_vars: List[str]) -> Tuple[Dict[str, Any], Any]:
        """执行多元线性回归
        
        Args:
            data: 数据
            dependent_var: 因变量
            independent_vars: 自变量列表
            
        Returns:
            Tuple[Dict[str, Any], Any]: 结果数据和模型
        """
        try:
            import statsmodels.api as sm
            from statsmodels.stats.outliers_influence import variance_inflation_factor
            
            # 准备数据
            X = data[independent_vars].values
            y = data[dependent_var].values
            
            # 添加常数项
            X_with_const = sm.add_constant(X)
            
            # 拟合模型
            model = sm.OLS(y, X_with_const).fit()
            
            # 获取结果
            params = model.params
            conf_int = model.conf_int()
            
            # 计算预测值和残差
            predictions = model.predict(X_with_const)
            residuals = y - predictions
            
            # 计算R方和调整R方
            r_squared = model.rsquared
            adj_r_squared = model.rsquared_adj
            
            # 计算F统计量和p值
            f_statistic = model.fvalue
            f_pvalue = model.f_pvalue
            
            # 计算标准误差
            std_errors = model.bse
            
            # 计算t统计量和p值
            t_values = model.tvalues
            p_values = model.pvalues
            
            # 计算AIC和BIC
            aic = model.aic
            bic = model.bic
            
            # 计算VIF
            vif_data = pd.DataFrame()
            vif_data["Variable"] = ["const"] + independent_vars
            vif_data["VIF"] = [variance_inflation_factor(X_with_const, i) for i in range(X_with_const.shape[1])]
            
            # 创建方程字符串
            equation = f"y = {params[0]:.4f}"
            for i, var in enumerate(independent_vars):
                if params[i+1] >= 0:
                    equation += f" + {params[i+1]:.4f}{var}"
                else:
                    equation += f" - {abs(params[i+1]):.4f}{var}"
                    
            # 创建结果数据
            result_data = {
                'model_summary': model.summary().as_text(),
                'coefficients': {var: params[i+1] for i, var in enumerate(independent_vars)},
                'intercept': params[0],
                'confidence_intervals': {var: (conf_int[i+1][0], conf_int[i+1][1]) 
                                       for i, var in enumerate(independent_vars)},
                'std_errors': {var: std_errors[i+1] for i, var in enumerate(independent_vars)},
                't_values': {var: t_values[i+1] for i, var in enumerate(independent_vars)},
                'p_values': {var: p_values[i+1] for i, var in enumerate(independent_vars)},
                'r_squared': r_squared,
                'adj_r_squared': adj_r_squared,
                'f_statistic': f_statistic,
                'f_pvalue': f_pvalue,
                'aic': aic,
                'bic': bic,
                'vif': vif_data.to_dict(orient='records'),
                'equation': equation,
                'predictions': predictions.tolist(),
                'residuals': residuals.tolist()
            }
            
            return result_data, model
        except ImportError:
            # 如果没有statsmodels，使用scikit-learn
            from sklearn.linear_model import LinearRegression
            from sklearn.metrics import r2_score, mean_squared_error
            
            # 准备数据
            X = data[independent_vars].values
            y = data[dependent_var].values
            
            # 拟合模型
            model = LinearRegression()
            model.fit(X, y)
            
            # 获取结果
            intercept = model.intercept_
            coefficients = model.coef_
            
            # 计算预测值和残差
            predictions = model.predict(X)
            residuals = y - predictions
            
            # 计算R方
            r_squared = r2_score(y, predictions)
            
            # 计算均方误差
            mse = mean_squared_error(y, predictions)
            
            # 创建方程字符串
            equation = f"y = {intercept:.4f}"
            for i, var in enumerate(independent_vars):
                if coefficients[i] >= 0:
                    equation += f" + {coefficients[i]:.4f}{var}"
                else:
                    equation += f" - {abs(coefficients[i]):.4f}{var}"
                    
            # 创建结果数据
            result_data = {
                'coefficients': {var: coefficients[i] for i, var in enumerate(independent_vars)},
                'intercept': intercept,
                'r_squared': r_squared,
                'mse': mse,
                'equation': equation,
                'predictions': predictions.tolist(),
                'residuals': residuals.tolist()
            }
            
            return result_data, model
            
    def _create_charts(self, data: pd.DataFrame, dependent_var: str, 
                      independent_vars: List[str], regression_type: RegressionType,
                      polynomial_degree: int, model: Any) -> Dict[str, Any]:
        """创建回归分析图表
        
        Args:
            data: 数据
            dependent_var: 因变量
            independent_vars: 自变量列表
            regression_type: 回归类型
            polynomial_degree: 多项式阶数
            model: 回归模型
            
        Returns:
            Dict[str, Any]: 包含图表对象的字典
        """
        charts = {}
        
        # 简单线性回归或多项式回归的图表
        if (regression_type == RegressionType.LINEAR or regression_type == RegressionType.POLYNOMIAL) and len(independent_vars) == 1:
            independent_var = independent_vars[0]
            
            # 创建散点图和回归线
            scatter = ScatterChart(title=f"{dependent_var} vs {independent_var}")
            scatter.set_data(data[independent_var].values, data[dependent_var].values)
            scatter.set_labels(x_label=independent_var, y_label=dependent_var)
            charts['scatter_plot'] = scatter
            
            # 创建回归线
            if regression_type == RegressionType.LINEAR:
                # 线性回归
                try:
                    # 对于statsmodels模型
                    intercept = model.params[0]
                    slope = model.params[1]
                    
                    # 创建回归线数据
                    x_min, x_max = data[independent_var].min(), data[independent_var].max()
                    x_range = np.linspace(x_min, x_max, 100)
                    y_pred = intercept + slope * x_range
                    
                    # 创建回归线图表
                    line = LineChart(title=f"{dependent_var} vs {independent_var} 回归线")
                    line.set_data(x_range, y_pred)
                    line.set_labels(x_label=independent_var, y_label=dependent_var)
                    charts['regression_line'] = line
                except AttributeError:
                    # 对于scikit-learn模型
                    intercept = model.intercept_
                    slope = model.coef_[0]
                    
                    # 创建回归线数据
                    x_min, x_max = data[independent_var].min(), data[independent_var].max()
                    x_range = np.linspace(x_min, x_max, 100)
                    y_pred = intercept + slope * x_range
                    
                    # 创建回归线图表
                    line = LineChart(title=f"{dependent_var} vs {independent_var} 回归线")
                    line.set_data(x_range, y_pred)
                    line.set_labels(x_label=independent_var, y_label=dependent_var)
                    charts['regression_line'] = line
            else:
                # 多项式回归
                try:
                    # 对于statsmodels模型
                    poly = model['poly']
                    model_fit = model['model']
                    
                    # 创建回归线数据
                    x_min, x_max = data[independent_var].min(), data[independent_var].max()
                    x_range = np.linspace(x_min, x_max, 100).reshape(-1, 1)
                    x_poly = poly.transform(x_range)
                    x_with_const = sm.add_constant(x_poly)
                    y_pred = model_fit.predict(x_with_const)
                    
                    # 创建回归线图表
                    line = LineChart(title=f"{dependent_var} vs {independent_var} 多项式回归线 (阶数={polynomial_degree})")
                    line.set_data(x_range.flatten(), y_pred)
                    line.set_labels(x_label=independent_var, y_label=dependent_var)
                    charts['regression_line'] = line
                except (AttributeError, TypeError):
                    # 对于scikit-learn模型
                    # 创建回归线数据
                    x_min, x_max = data[independent_var].min(), data[independent_var].max()
                    x_range = np.linspace(x_min, x_max, 100).reshape(-1, 1)
                    y_pred = model.predict(x_range)
                    
                    # 创建回归线图表
                    line = LineChart(title=f"{dependent_var} vs {independent_var} 多项式回归线 (阶数={polynomial_degree})")
                    line.set_data(x_range.flatten(), y_pred)
                    line.set_labels(x_label=independent_var, y_label=dependent_var)
                    charts['regression_line'] = line
                    
            # 创建残差图
            try:
                # 对于statsmodels模型
                predictions = model.predict(sm.add_constant(data[independent_var].values.reshape(-1, 1)))
                residuals = data[dependent_var].values - predictions
            except (AttributeError, TypeError):
                # 对于scikit-learn模型
                predictions = model.predict(data[independent_var].values.reshape(-1, 1))
                residuals = data[dependent_var].values - predictions
                
            # 创建残差散点图
            residual_scatter = ScatterChart(title=f"{dependent_var} vs {independent_var} 残差图")
            residual_scatter.set_data(predictions, residuals)
            residual_scatter.set_labels(x_label="预测值", y_label="残差")
            charts['residual_plot'] = residual_scatter
            
        # 多元线性回归的图表
        elif regression_type == RegressionType.MULTIPLE or len(independent_vars) > 1:
            # 创建预测值vs实际值散点图
            try:
                # 对于statsmodels模型
                X_with_const = sm.add_constant(data[independent_vars].values)
                predictions = model.predict(X_with_const)
            except (AttributeError, TypeError):
                # 对于scikit-learn模型
                predictions = model.predict(data[independent_vars].values)
                
            actual = data[dependent_var].values
            
            # 创建散点图
            scatter = ScatterChart(title=f"{dependent_var} 预测值 vs 实际值")
            scatter.set_data(predictions, actual)
            scatter.set_labels(x_label="预测值", y_label="实际值")
            charts['scatter_plot'] = scatter
            
            # 创建残差图
            residuals = actual - predictions
            
            # 创建残差散点图
            residual_scatter = ScatterChart(title=f"{dependent_var} 残差图")
            residual_scatter.set_data(predictions, residuals)
            residual_scatter.set_labels(x_label="预测值", y_label="残差")
            charts['residual_plot'] = residual_scatter
            
        return charts
        
    def predict(self, new_data: Union[pd.DataFrame, Dict[str, Any]]) -> np.ndarray:
        """使用回归模型进行预测
        
        Args:
            new_data: 新数据，可以是DataFrame或字典
            
        Returns:
            np.ndarray: 预测结果
            
        Raises:
            ValueError: 如果模型未训练或数据无效
        """
        if self.model is None:
            raise ValueError("模型未训练，请先调用analyze方法")
            
        # 获取模型参数
        dependent_var = self.model_params['dependent_var']
        independent_vars = self.model_params['independent_vars']
        regression_type = self.model_params['regression_type']
        polynomial_degree = self.model_params.get('polynomial_degree', 2)
        
        # 将输入转换为DataFrame
        if isinstance(new_data, dict):
            new_data = pd.DataFrame([new_data])
            
        # 验证输入数据
        for var in independent_vars:
            if var not in new_data.columns:
                raise ValueError(f"输入数据缺少变量: {var}")
                
        # 根据回归类型进行预测
        if regression_type == RegressionType.LINEAR and len(independent_vars) == 1:
            # 简单线性回归
            independent_var = independent_vars[0]
            X = new_data[independent_var].values.reshape(-1, 1)
            
            try:
                # 对于statsmodels模型
                import statsmodels.api as sm
                X_with_const = sm.add_constant(X)
                return self.model.predict(X_with_const)
            except (AttributeError, ImportError):
                # 对于scikit-learn模型
                return self.model.predict(X)
                
        elif regression_type == RegressionType.POLYNOMIAL and len(independent_vars) == 1:
            # 多项式回归
            independent_var = independent_vars[0]
            X = new_data[independent_var].values.reshape(-1, 1)
            
            try:
                # 对于statsmodels模型
                import statsmodels.api as sm
                poly = self.model['poly']
                model_fit = self.model['model']
                
                X_poly = poly.transform(X)
                X_with_const = sm.add_constant(X_poly)
                return model_fit.predict(X_with_const)
            except (AttributeError, TypeError, ImportError):
                # 对于scikit-learn模型
                return self.model.predict(X)
                
        elif regression_type == RegressionType.MULTIPLE or len(independent_vars) > 1:
            # 多元线性回归
            X = new_data[independent_vars].values
            
            try:
                # 对于statsmodels模型
                import statsmodels.api as sm
                X_with_const = sm.add_constant(X)
                return self.model.predict(X_with_const)
            except (AttributeError, ImportError):
                # 对于scikit-learn模型
                return self.model.predict(X)
                
        else:
            raise ValueError(f"不支持的回归类型: {regression_type}")
            
    def model_diagnostics(self) -> Dict[str, Any]:
        """执行模型诊断
        
        Returns:
            Dict[str, Any]: 诊断结果
            
        Raises:
            ValueError: 如果模型未训练
        """
        if self.model is None:
            raise ValueError("模型未训练，请先调用analyze方法")
            
        # 获取模型参数
        dependent_var = self.model_params['dependent_var']
        independent_vars = self.model_params['independent_vars']
        regression_type = self.model_params['regression_type']
        
        # 获取数据
        df = self.dataset.data
        
        # 准备数据
        if len(independent_vars) == 1:
            X = df[independent_vars[0]].values.reshape(-1, 1)
        else:
            X = df[independent_vars].values
            
        y = df[dependent_var].values
        
        # 尝试使用statsmodels进行诊断
        try:
            import statsmodels.api as sm
            from statsmodels.stats.diagnostic import het_breuschpagan, acorr_ljungbox
            from statsmodels.stats.stattools import durbin_watson
            from statsmodels.stats.outliers_influence import variance_inflation_factor
            
            # 获取模型
            if isinstance(self.model, dict) and 'model' in self.model:
                model = self.model['model']
            else:
                model = self.model
                
            # 获取残差
            if hasattr(model, 'resid'):
                residuals = model.resid
            else:
                # 对于scikit-learn模型，手动计算残差
                if regression_type == RegressionType.POLYNOMIAL and len(independent_vars) == 1:
                    # 多项式回归
                    poly = self.model['poly']
                    X_poly = poly.transform(X)
                    X_with_const = sm.add_constant(X_poly)
                    predictions = model.predict(X_with_const)
                elif len(independent_vars) == 1:
                    # 简单线性回归
                    X_with_const = sm.add_constant(X)
                    predictions = model.predict(X_with_const)
                else:
                    # 多元线性回归
                    X_with_const = sm.add_constant(X)
                    predictions = model.predict(X_with_const)
                    
                residuals = y - predictions
                
            # 计算诊断统计量
            # 1. 异方差性检验（Breusch-Pagan检验）
            bp_test = het_breuschpagan(residuals, sm.add_constant(X))
            bp_test_result = {
                'lagrange_multiplier': bp_test[0],
                'p_value': bp_test[1],
                'f_value': bp_test[2],
                'f_p_value': bp_test[3]
            }
            
            # 2. 自相关检验（Ljung-Box检验）
            lb_test = acorr_ljungbox(residuals, lags=[1])
            lb_test_result = {
                'lb_statistic': lb_test[0][0],
                'lb_p_value': lb_test[1][0]
            }
            
            # 3. Durbin-Watson检验
            dw_test = durbin_watson(residuals)
            
            # 4. 多重共线性检验（VIF）
            if len(independent_vars) > 1:
                vif_data = pd.DataFrame()
                vif_data["Variable"] = ["const"] + independent_vars
                vif_data["VIF"] = [variance_inflation_factor(sm.add_constant(X), i) 
                                 for i in range(sm.add_constant(X).shape[1])]
                vif_result = vif_data.to_dict(orient='records')
            else:
                vif_result = None
                
            # 5. 正态性检验（Jarque-Bera检验）
            jb_test = stats.jarque_bera(residuals)
            jb_test_result = {
                'jb_statistic': jb_test[0],
                'jb_p_value': jb_test[1]
            }
            
            # 创建诊断结果
            diagnostics = {
                'heteroscedasticity_test': bp_test_result,
                'autocorrelation_test': lb_test_result,
                'durbin_watson': dw_test,
                'multicollinearity_test': vif_result,
                'normality_test': jb_test_result
            }
            
            return diagnostics
        except ImportError:
            # 如果没有statsmodels，使用基本诊断
            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
            
            # 获取预测值
            if regression_type == RegressionType.POLYNOMIAL and len(independent_vars) == 1:
                # 多项式回归
                predictions = self.model.predict(X)
            elif len(independent_vars) == 1:
                # 简单线性回归
                predictions = self.model.predict(X)
            else:
                # 多元线性回归
                predictions = self.model.predict(X)
                
            # 计算残差
            residuals = y - predictions
            
            # 计算基本指标
            mse = mean_squared_error(y, predictions)
            mae = mean_absolute_error(y, predictions)
            r2 = r2_score(y, predictions)
            
            # 创建诊断结果
            diagnostics = {
                'mse': mse,
                'mae': mae,
                'r2': r2,
                'residuals_mean': np.mean(residuals),
                'residuals_std': np.std(residuals)
            }
            
            return diagnostics
            
    def _logistic_regression(self, data: pd.DataFrame, dependent_var: str, 
                           independent_vars: List[str]) -> Tuple[Dict[str, Any], Any]:
        """执行逻辑回归
        
        Args:
            data: 数据
            dependent_var: 因变量（二分类变量）
            independent_vars: 自变量列表
            
        Returns:
            Tuple[Dict[str, Any], Any]: 结果数据和模型
        """
        try:
            import statsmodels.api as sm
            from statsmodels.discrete.discrete_model import Logit
            
            # 准备数据
            X = data[independent_vars].values
            y = data[dependent_var].values
            
            # 添加常数项
            X_with_const = sm.add_constant(X)
            
            # 拟合模型
            model = Logit(y, X_with_const).fit()
            
            # 获取结果
            params = model.params
            conf_int = model.conf_int()
            
            # 计算预测值和概率
            predictions_prob = model.predict(X_with_const)
            predictions = (predictions_prob > 0.5).astype(int)
            
            # 计算分类指标
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score
            
            accuracy = accuracy_score(y, predictions)
            precision = precision_score(y, predictions, zero_division=0)
            recall = recall_score(y, predictions, zero_division=0)
            f1 = f1_score(y, predictions, zero_division=0)
            conf_matrix = confusion_matrix(y, predictions)
            try:
                auc = roc_auc_score(y, predictions_prob)
            except:
                auc = None
            
            # 创建结果数据
            result_data = {
                'model_summary': model.summary().as_text(),
                'coefficients': {var: params[i+1] for i, var in enumerate(independent_vars)},
                'intercept': params[0],
                'confidence_intervals': {var: (conf_int[i+1][0], conf_int[i+1][1]) 
                                       for i, var in enumerate(independent_vars)},
                'p_values': {var: model.pvalues[i+1] for i, var in enumerate(independent_vars)},
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'confusion_matrix': conf_matrix.tolist(),
                'auc': auc,
                'predictions': predictions.tolist(),
                'prediction_probs': predictions_prob.tolist()
            }
            
            return result_data, model
        except ImportError:
            # 如果没有statsmodels，使用scikit-learn
            from sklearn.linear_model import LogisticRegression
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score
            
            # 准备数据
            X = data[independent_vars].values
            y = data[dependent_var].values
            
            # 拟合模型
            model = LogisticRegression(max_iter=1000)
            model.fit(X, y)
            
            # 获取结果
            intercept = model.intercept_[0]
            coefficients = model.coef_[0]
            
            # 计算预测值和概率
            predictions_prob = model.predict_proba(X)[:, 1]
            predictions = model.predict(X)
            
            # 计算分类指标
            accuracy = accuracy_score(y, predictions)
            precision = precision_score(y, predictions, zero_division=0)
            recall = recall_score(y, predictions, zero_division=0)
            f1 = f1_score(y, predictions, zero_division=0)
            conf_matrix = confusion_matrix(y, predictions)
            try:
                auc = roc_auc_score(y, predictions_prob)
            except:
                auc = None
            
            # 创建方程字符串
            equation = f"log(p/(1-p)) = {intercept:.4f}"
            for i, var in enumerate(independent_vars):
                if coefficients[i] >= 0:
                    equation += f" + {coefficients[i]:.4f}{var}"
                else:
                    equation += f" - {abs(coefficients[i]):.4f}{var}"
            
            # 创建模型摘要字符串
            model_summary = f"Logistic Regression Results:\n\n"
            model_summary += f"Dependent Variable: {dependent_var}\n"
            model_summary += f"Independent Variables: {', '.join(independent_vars)}\n\n"
            model_summary += f"Intercept: {intercept:.6f}\n"
            for i, var in enumerate(independent_vars):
                model_summary += f"{var}: {coefficients[i]:.6f}\n"
            model_summary += f"\nAccuracy: {accuracy:.6f}\n"
            model_summary += f"Precision: {precision:.6f}\n"
            model_summary += f"Recall: {recall:.6f}\n"
            model_summary += f"F1 Score: {f1:.6f}\n"
            if auc is not None:
                model_summary += f"AUC: {auc:.6f}\n"
            
            # 创建结果数据
            result_data = {
                'model_summary': model_summary,
                'coefficients': {var: coefficients[i] for i, var in enumerate(independent_vars)},
                'intercept': intercept,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'confusion_matrix': conf_matrix.tolist(),
                'auc': auc,
                'equation': equation,
                'predictions': predictions.tolist(),
                'prediction_probs': predictions_prob.tolist()
            }
            
            return result_data, model