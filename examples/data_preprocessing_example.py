"""
数据预处理示例 - 展示如何使用DataPreprocessor类进行数据清洗和转换
"""

import numpy as np
import pandas as pd
from scientific_analysis.data import (
    DataPreprocessor, 
    MissingValueStrategy,  # 缺失值处理策略
    DataType,              # 数据类型定义
    NormalizationMethod    # 标准化方法
)

def main():
    """
    主函数 - 演示数据预处理流程
    1. 创建包含各种数据类型的示例数据
    2. 处理缺失值
    3. 转换数据类型
    4. 应用标准化
    5. 保存处理结果
    """
    # 创建样本数据
    data = {
        # 数值型数据（含缺失值）
        'age': [25, 30, np.nan, 45, 22, 60, 29, 41, 19, 50],
        'income': [50000, 75000, 80000, np.nan, 30000, 120000, 68000, 92000, 25000, 110000],
        # 分类数据
        'department': ['HR', 'IT', 'IT', 'Finance', 'HR', 'IT', 'Finance', 'Finance', 'HR', 'IT'],
        # 布尔型数据
        'is_manager': [False, True, False, True, False, True, False, True, False, False],
        # 日期字符串
        'join_date': ['2020-01-15', '2019-05-20', '2021-03-10', '2018-11-05', 
                     '2022-02-28', '2017-07-15', '2020-09-10', '2019-12-01', '2022-01-10', '2018-06-20']
    }
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    print("原始数据:")
    print(df)
    print("\n" + "="*80 + "\n")
    
    # 创建数据预处理器实例
    preprocessor = DataPreprocessor(df)
    
    # 1. 处理缺失值
    preprocessor.handle_missing_values(
        strategy_dict={
            'age': MissingValueStrategy.FILL_MEDIAN,    # 年龄用中位数填充
            'income': MissingValueStrategy.FILL_MEAN    # 收入用平均值填充
        }
    )
    
    # 2. 转换数据类型
    preprocessor.convert_data_types(
        type_dict={
            'join_date': DataType.DATETIME,  # 转换为日期时间类型
            'department': DataType.CATEGORY  # 转换为分类类型
        }
    )
    
    # 3. 标准化数值列
    preprocessor.normalize_data(
        columns=['age', 'income'],
        method=NormalizationMethod.STANDARD  # 使用Z-score标准化
    )
    
    # 获取并显示处理后的数据
    processed_df = preprocessor.get_processed_data()
    print("处理后的数据:")
    print(processed_df)
    
    # 保存处理结果
    processed_df.to_csv('processed_data.csv', index=False)
    print("\n处理结果已保存到 processed_data.csv")

if __name__ == "__main__":
    main()