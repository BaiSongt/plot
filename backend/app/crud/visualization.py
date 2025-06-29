from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from ..models.visualization import Visualization
from ..schemas.visualization import VisualizationCreate, VisualizationUpdate

def get_visualization(db: Session, visualization_id: int) -> Optional[Visualization]:
    """通过ID获取单个可视化"""
    return db.query(Visualization).filter(Visualization.id == visualization_id).first()

def get_visualizations_by_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[Visualization]:
    """获取用户的所有可视化"""
    return (
        db.query(Visualization)
        .filter(Visualization.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_visualization(
    db: Session, visualization: VisualizationCreate, user_id: int
) -> Visualization:
    """创建新的可视化"""
    db_visualization = Visualization(
        **visualization.dict(),
        user_id=user_id
    )
    db.add(db_visualization)
    db.commit()
    db.refresh(db_visualization)
    return db_visualization

def update_visualization(
    db: Session, 
    db_visualization: Visualization, 
    visualization_in: VisualizationUpdate
) -> Visualization:
    """更新可视化"""
    update_data = visualization_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_visualization, field, value)
    db.add(db_visualization)
    db.commit()
    db.refresh(db_visualization)
    return db_visualization

def delete_visualization(db: Session, visualization_id: int) -> bool:
    """删除可视化"""
    visualization = get_visualization(db, visualization_id)
    if not visualization:
        return False
    db.delete(visualization)
    db.commit()
    return True
