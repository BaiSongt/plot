import os
import sys
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 将项目根目录添加到 Python 路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.db.base_class import Base
from app.main import app

# 使用测试数据库
TEST_DATABASE_URL = "sqlite:///./test.db"

# 配置测试数据库
engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建测试数据库表
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="session")
def db() -> Generator:
    """数据库会话fixture"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 创建测试会话
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # 测试结束后删除测试数据库
        if os.path.exists("test.db"):
            os.remove("test.db")

@pytest.fixture(scope="module")
def client() -> Generator:
    """测试客户端fixture"""
    # 临时覆盖数据库URL
    original_db_url = settings.DATABASE_URL
    settings.DATABASE_URL = TEST_DATABASE_URL
    
    # 创建测试客户端
    with TestClient(app) as test_client:
        yield test_client
    
    # 恢复原始数据库URL
    settings.DATABASE_URL = original_db_url

@pytest.fixture(scope="module")
def test_user() -> dict:
    """测试用户fixture"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123"
    }
