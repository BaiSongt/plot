#!/usr/bin/env python3
"""
数据集管理API端点
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
import pandas as pd
import json
import io

from ...db.database import get_db
from ...models.user import User
from ...api.dependencies import get_current_active_user
from ...schemas.dataset import DatasetCreate, DatasetResponse, DatasetUpdate, DatasetSummary
from ...models.dataset import Dataset

router = APIRouter()

@router.post("/upload-test", status_code=status.HTTP_201_CREATED)
async def upload_dataset_test(
    file: UploadFile = File(...),
    name: Optional[str] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """测试用数据上传接口（无需认证）"""
    try:
        # 检查文件类型
        allowed_extensions = ['.csv', '.json', '.xlsx', '.xls']
        file_extension = None
        for ext in allowed_extensions:
            if file.filename.lower().endswith(ext):
                file_extension = ext
                break
        
        if not file_extension:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件格式。支持的格式: {', '.join(allowed_extensions)}"
            )
        
        # 读取文件内容
        content = await file.read()
        
        # 根据文件类型解析数据
        df = None
        if file_extension == '.csv':
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        elif file_extension == '.json':
            data = json.loads(content.decode('utf-8'))
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                raise ValueError("JSON文件格式不正确")
        elif file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(io.BytesIO(content))
        
        if df is None or df.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件为空或无法解析"
            )
        
        # 处理数据
        # 将NaN值转换为None以便JSON序列化
        df_clean = df.where(pd.notnull(df), None)
        
        # 准备数据集信息
        dataset_name = name or file.filename.rsplit('.', 1)[0]
        dataset_data = df_clean.to_dict('records')
        columns = list(df.columns)
        shape = list(df.shape)
        dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
        
        return {
            "message": "文件上传成功",
            "filename": file.filename,
            "name": dataset_name,
            "description": description or f"从文件 {file.filename} 上传的数据集",
            "columns": columns,
            "shape": shape,
            "dtypes": dtypes,
            "sample_data": dataset_data[:5]  # 返回前5行作为示例
        }
        
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件为空"
        )
    except pd.errors.ParserError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件解析错误: {str(e)}"
        )
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件编码错误，请确保文件为UTF-8编码"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传失败: {str(e)}"
        )

@router.post("/upload", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    name: Optional[str] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """上传数据集文件"""
    try:
        # 检查文件类型
        allowed_extensions = ['.csv', '.json', '.xlsx', '.xls']
        file_extension = None
        for ext in allowed_extensions:
            if file.filename.lower().endswith(ext):
                file_extension = ext
                break
        
        if not file_extension:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件格式。支持的格式: {', '.join(allowed_extensions)}"
            )
        
        # 读取文件内容
        content = await file.read()
        
        # 根据文件类型解析数据
        df = None
        if file_extension == '.csv':
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        elif file_extension == '.json':
            data = json.loads(content.decode('utf-8'))
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                raise ValueError("JSON文件格式不正确")
        elif file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(io.BytesIO(content))
        
        if df is None or df.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件为空或无法解析"
            )
        
        # 处理数据
        # 将NaN值转换为None以便JSON序列化
        df_clean = df.where(pd.notnull(df), None)
        
        # 准备数据集信息
        dataset_name = name or file.filename.rsplit('.', 1)[0]
        dataset_data = df_clean.to_dict('records')
        columns = list(df.columns)
        shape = list(df.shape)
        dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
        
        # 创建数据集记录
        db_dataset = Dataset(
            name=dataset_name,
            description=description or f"从文件 {file.filename} 上传的数据集",
            data=dataset_data,
            columns=columns,
            shape=shape,
            dtypes=dtypes,
            owner_id=current_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(db_dataset)
        db.commit()
        db.refresh(db_dataset)
        
        return db_dataset
        
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件为空"
        )
    except pd.errors.ParserError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件解析错误: {str(e)}"
        )
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件编码错误，请确保文件为UTF-8编码"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传失败: {str(e)}"
        )

@router.post("/", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
def create_dataset(
    dataset: DatasetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建新数据集"""
    try:
        # 创建数据集记录
        db_dataset = Dataset(
            name=dataset.name,
            description=dataset.description,
            data=dataset.data,
            columns=dataset.columns,
            shape=dataset.shape,
            dtypes=dataset.dtypes,
            owner_id=current_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(db_dataset)
        db.commit()
        db.refresh(db_dataset)
        
        return db_dataset
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建数据集失败: {str(e)}"
        )

@router.get("/", response_model=List[DatasetResponse])
def get_datasets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的所有数据集"""
    datasets = db.query(Dataset).filter(
        Dataset.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return datasets

@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取特定数据集"""
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.owner_id == current_user.id
    ).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据集不存在"
        )
    
    return dataset

@router.put("/{dataset_id}", response_model=DatasetResponse)
def update_dataset(
    dataset_id: int,
    dataset_update: DatasetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新数据集"""
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.owner_id == current_user.id
    ).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据集不存在"
        )
    
    try:
        # 更新字段
        update_data = dataset_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(dataset, field, value)
        
        dataset.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(dataset)
        
        return dataset
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新数据集失败: {str(e)}"
        )

@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除数据集"""
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.owner_id == current_user.id
    ).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据集不存在"
        )
    
    try:
        db.delete(dataset)
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"删除数据集失败: {str(e)}"
        )

@router.post("/{dataset_id}/analyze")
def analyze_dataset(
    dataset_id: int,
    analysis_type: str,
    parameters: dict = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """分析数据集"""
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.owner_id == current_user.id
    ).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据集不存在"
        )
    
    try:
        # 这里可以添加具体的分析逻辑
        import pandas as pd
        import numpy as np
        
        # 将数据转换为DataFrame
        df = pd.DataFrame(dataset.data)
        
        result = {}
        
        if analysis_type == "basic_stats":
            # 基础统计信息
            result = {
                "shape": df.shape,
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "missing_values": df.isnull().sum().to_dict(),
                "numeric_summary": df.describe().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 0 else {},
                "memory_usage": df.memory_usage(deep=True).to_dict()
            }
        
        elif analysis_type == "correlation":
            # 相关性分析
            numeric_df = df.select_dtypes(include=[np.number])
            if len(numeric_df.columns) > 1:
                result = {
                    "correlation_matrix": numeric_df.corr().to_dict(),
                    "correlation_pairs": []
                }
                
                # 找出高相关性的变量对
                corr_matrix = numeric_df.corr()
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_value = corr_matrix.iloc[i, j]
                        if abs(corr_value) > 0.7:  # 高相关性阈值
                            result["correlation_pairs"].append({
                                "var1": corr_matrix.columns[i],
                                "var2": corr_matrix.columns[j],
                                "correlation": corr_value
                            })
            else:
                result = {"error": "数据集中数值列少于2个，无法进行相关性分析"}
        
        elif analysis_type == "outliers":
            # 异常值检测
            numeric_df = df.select_dtypes(include=[np.number])
            outliers = {}
            
            for col in numeric_df.columns:
                Q1 = numeric_df[col].quantile(0.25)
                Q3 = numeric_df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_indices = numeric_df[
                    (numeric_df[col] < lower_bound) | (numeric_df[col] > upper_bound)
                ].index.tolist()
                
                outliers[col] = {
                    "count": len(outlier_indices),
                    "indices": outlier_indices[:10],  # 只返回前10个
                    "bounds": {"lower": lower_bound, "upper": upper_bound}
                }
            
            result = {"outliers": outliers}
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的分析类型: {analysis_type}"
            )
        
        return {
            "dataset_id": dataset_id,
            "analysis_type": analysis_type,
            "parameters": parameters,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {str(e)}"
        )