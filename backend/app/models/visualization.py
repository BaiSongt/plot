from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Visualization(Base):
    """数据可视化模型"""
    __tablename__ = "visualizations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    chart_type = Column(String(50), nullable=False)  # 如: line, bar, scatter, surface 等
    data_config = Column(JSON, nullable=False)  # 存储图表配置
    style_config = Column(JSON, nullable=True)  # 存储样式配置
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 关系
    user = relationship("User", back_populates="visualizations")
