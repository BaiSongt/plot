import pandas as pd
import numpy as np
from typing import Dict, Any
from sklearn.ensemble import IsolationForest
from scipy import stats

def detect_outliers_iqr(data: pd.DataFrame, threshold: float = 1.5) -> Dict[str, Any]:
    """使用IQR方法检测异常值
    
    Args:
        data: 输入数据
        threshold: IQR阈值倍数
        
    Returns:
        Dict[str, Any]: 异常值检测结果
    """
    outliers = {}
    
    for column in data.columns:
        col_data = data[column]
        q1 = col_data.quantile(0.25)
        q3 = col_data.quantile(0.75)
        iqr = q3 - q1
        
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        
        is_outlier = (col_data < lower_bound) | (col_data > upper_bound)
        outlier_indices = col_data[is_outlier].index.tolist()
        
        outliers[column] = {
            'is_outlier': is_outlier,  # 这已经是pandas Series
            'outlier_indices': outlier_indices,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'outlier_count': len(outlier_indices)
        }
    
    return outliers

def detect_outliers_zscore(data: pd.DataFrame, threshold: float = 3.0) -> Dict[str, Any]:
    """使用Z-score方法检测异常值
    
    Args:
        data: 输入数据
        threshold: Z-score阈值
        
    Returns:
        Dict[str, Any]: 异常值检测结果
    """
    outliers = {}
    
    for column in data.columns:
        col_data = data[column]
        z_scores = np.abs(stats.zscore(col_data))
        
        is_outlier = pd.Series(z_scores > threshold, index=col_data.index)
        outlier_indices = col_data[is_outlier].index.tolist()
        
        outliers[column] = {
            'is_outlier': is_outlier,
            'outlier_indices': outlier_indices,
            'z_scores': pd.Series(z_scores, index=col_data.index),
            'threshold': threshold,
            'outlier_count': len(outlier_indices)
        }
    
    return outliers

def detect_outliers_isolation(data: pd.DataFrame, contamination: float = 0.1) -> Dict[str, Any]:
    """使用Isolation Forest方法检测异常值
    
    Args:
        data: 输入数据
        contamination: 异常值比例
        
    Returns:
        Dict[str, Any]: 异常值检测结果
    """
    outliers = {}
    
    for column in data.columns:
        col_data = data[column].values.reshape(-1, 1)
        
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        outlier_labels = iso_forest.fit_predict(col_data)
        
        is_outlier = outlier_labels == -1
        outlier_indices = data.index[is_outlier].tolist()
        
        outliers[column] = {
            'is_outlier': pd.Series(is_outlier, index=data.index),
            'outlier_indices': outlier_indices,
            'outlier_scores': iso_forest.decision_function(col_data),
            'contamination': contamination,
            'outlier_count': len(outlier_indices)
        }
    
    return outliers