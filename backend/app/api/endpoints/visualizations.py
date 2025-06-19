from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.deps import get_db, get_current_active_user

router = APIRouter()

@router.post("/", response_model=schemas.Visualization, status_code=status.HTTP_201_CREATED)
def create_visualization(
    visualization_in: schemas.VisualizationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    创建新的可视化
    
    - **title**: 可视化标题
    - **description**: 可视化描述（可选）
    - **chart_type**: 图表类型（line, bar, scatter, surface等）
    - **data_config**: 数据配置（JSON格式）
    - **style_config**: 样式配置（可选，JSON格式）
    """
    return crud.create_visualization(
        db=db, 
        visualization=visualization_in, 
        user_id=current_user.id
    )

@router.get("/", response_model=List[schemas.Visualization])
def read_visualizations(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    获取当前用户的所有可视化
    
    - **skip**: 跳过的记录数（分页用）
    - **limit**: 每页返回的记录数（分页用）
    """
    visualizations = crud.get_visualizations_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return visualizations

@router.get("/{visualization_id}", response_model=schemas.Visualization)
def read_visualization(
    visualization_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    通过ID获取单个可视化
    
    - **visualization_id**: 可视化ID
    """
    visualization = crud.get_visualization(db, visualization_id=visualization_id)
    if not visualization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到该可视化"
        )
    if visualization.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问该可视化"
        )
    return visualization

@router.put("/{visualization_id}", response_model=schemas.Visualization)
def update_visualization(
    visualization_id: int,
    visualization_in: schemas.VisualizationUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    更新可视化
    
    - **visualization_id**: 要更新的可视化ID
    - **title**: 新标题（可选）
    - **description**: 新描述（可选）
    - **chart_type**: 新图表类型（可选）
    - **data_config**: 新数据配置（可选）
    - **style_config**: 新样式配置（可选）
    """
    visualization = crud.get_visualization(db, visualization_id=visualization_id)
    if not visualization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到该可视化"
        )
    if visualization.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限更新该可视化"
        )
    return crud.update_visualization(
        db=db, 
        db_visualization=visualization, 
        visualization_in=visualization_in
    )

@router.delete("/{visualization_id}", response_model=schemas.Visualization)
def delete_visualization(
    visualization_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    删除可视化
    
    - **visualization_id**: 要删除的可视化ID
    """
    visualization = crud.get_visualization(db, visualization_id=visualization_id)
    if not visualization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到该可视化"
        )
    if visualization.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除该可视化"
        )
    crud.delete_visualization(db, visualization_id=visualization_id)
    return visualization
