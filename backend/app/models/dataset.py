#!/usr/bin/env python3
"""
数据集模型
"""

from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from ..db.base_class import Base

class Dataset(Base):
    """数据集模型"""
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # 数据内容（JSON格式存储）
    data = Column(JSON, nullable=False)
    
    # 元数据
    columns = Column(JSON, nullable=False)  # 列名列表
    shape = Column(JSON, nullable=False)    # 数据形状 [rows, cols]
    dtypes = Column(JSON, nullable=False)   # 数据类型字典
    
    # 关联用户
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="datasets")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Dataset(id={self.id}, name='{self.name}', owner_id={self.owner_id})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "data": self.data,
            "columns": self.columns,
            "shape": self.shape,
            "dtypes": self.dtypes,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }