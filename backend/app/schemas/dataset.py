#!/usr/bin/env python3
"""
数据集Schema定义
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class DatasetBase(BaseModel):
    """数据集基础Schema"""
    name: str = Field(..., min_length=1, max_length=255, description="数据集名称")
    description: Optional[str] = Field(None, description="数据集描述")

class DatasetCreate(DatasetBase):
    """创建数据集Schema"""
    data: List[Dict[str, Any]] = Field(..., description="数据内容")
    columns: List[str] = Field(..., description="列名列表")
    shape: List[int] = Field(..., description="数据形状 [rows, cols]")
    dtypes: Dict[str, str] = Field(..., description="数据类型字典")

class DatasetUpdate(BaseModel):
    """更新数据集Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="数据集名称")
    description: Optional[str] = Field(None, description="数据集描述")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="数据内容")
    columns: Optional[List[str]] = Field(None, description="列名列表")
    shape: Optional[List[int]] = Field(None, description="数据形状 [rows, cols]")
    dtypes: Optional[Dict[str, str]] = Field(None, description="数据类型字典")

class DatasetResponse(DatasetBase):
    """数据集响应Schema"""
    id: int
    data: List[Dict[str, Any]]
    columns: List[str]
    shape: List[int]
    dtypes: Dict[str, str]
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DatasetSummary(BaseModel):
    """数据集摘要Schema（不包含具体数据）"""
    id: int
    name: str
    description: Optional[str]
    columns: List[str]
    shape: List[int]
    dtypes: Dict[str, str]
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DatasetAnalysisRequest(BaseModel):
    """数据集分析请求Schema"""
    analysis_type: str = Field(..., description="分析类型")
    parameters: Optional[Dict[str, Any]] = Field(None, description="分析参数")

class DatasetAnalysisResponse(BaseModel):
    """数据集分析响应Schema"""
    dataset_id: int
    analysis_type: str
    parameters: Optional[Dict[str, Any]]
    result: Dict[str, Any]
    timestamp: datetime