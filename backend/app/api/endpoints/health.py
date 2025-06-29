#!/usr/bin/env python3
"""
健康检查API端点
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import psutil
import os

from ...db.database import get_db

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """健康检查端点"""
    try:
        # 检查数据库连接
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # 获取系统信息
    system_info = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent,
        "process_count": len(psutil.pids())
    }
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
        "system": system_info,
        "version": "1.0.0"
    }

@router.get("/ping")
def ping():
    """简单的ping端点"""
    return {
        "message": "pong",
        "timestamp": datetime.utcnow().isoformat()
    }