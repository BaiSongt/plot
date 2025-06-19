from typing import Dict, Optional

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User

def get_user_authentication_headers(
    client: TestClient, 
    username: str, 
    password: str
) -> Dict[str, str]:
    """
    获取用户的认证头
    
    参数:
        client: 测试客户端
        username: 用户名
        password: 密码
        
    返回:
        包含认证头的字典
    """
    login_data = {
        "username": username,
        "password": password,
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    tokens = response.json()
    access_token = tokens["access_token"]
    return {"Authorization": f"Bearer {access_token}"}

def create_test_user(
    db: Session, 
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "testpass123",
    is_superuser: bool = False,
    is_active: bool = True,
) -> User:
    """
    创建测试用户
    
    参数:
        db: 数据库会话
        username: 用户名
        email: 电子邮箱
        password: 密码
        is_superuser: 是否超级用户
        is_active: 是否激活
        
    返回:
        创建的用户对象
    """
    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        is_superuser=is_superuser,
        is_active=is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_test_user_and_token(
    client: TestClient,
    db: Session,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "testpass123",
    is_superuser: bool = False,
    is_active: bool = True,
) -> tuple[User, Dict[str, str]]:
    """
    创建测试用户并获取认证头
    
    参数:
        client: 测试客户端
        db: 数据库会话
        username: 用户名
        email: 电子邮箱
        password: 密码
        is_superuser: 是否超级用户
        is_active: 是否激活
        
    返回:
        元组 (用户对象, 认证头)
    """
    user = create_test_user(
        db=db,
        username=username,
        email=email,
        password=password,
        is_superuser=is_superuser,
        is_active=is_active,
    )
    headers = get_user_authentication_headers(
        client=client,
        username=username,
        password=password,
    )
    return user, headers
