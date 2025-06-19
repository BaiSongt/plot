from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class VisualizationBase(BaseModel):
    """可视化基础模型"""
    title: str = Field(..., max_length=255, description="可视化标题")
    description: Optional[str] = Field(None, description="可视化描述")
    chart_type: str = Field(..., description="图表类型，如：line, bar, scatter, surface等")
    data_config: Dict[str, Any] = Field(..., description="数据配置")
    style_config: Optional[Dict[str, Any]] = Field(None, description="样式配置")

class VisualizationCreate(VisualizationBase):
    """创建可视化模型"""
    pass

class VisualizationUpdate(BaseModel):
    """更新可视化模型"""
    title: Optional[str] = Field(None, max_length=255, description="可视化标题")
    description: Optional[str] = Field(None, description="可视化描述")
    chart_type: Optional[str] = Field(None, description="图表类型")
    data_config: Optional[Dict[str, Any]] = Field(None, description="数据配置")
    style_config: Optional[Dict[str, Any]] = Field(None, description="样式配置")

class VisualizationInDBBase(VisualizationBase):
    """数据库中的可视化模型"""
    id: int
    user_id: int

    class Config:
        orm_mode = True

class Visualization(VisualizationInDBBase):
    """响应模型"""
    pass
