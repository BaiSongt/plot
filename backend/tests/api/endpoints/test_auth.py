import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User

# 测试用户注册
def test_register_user(client, db: Session, test_user: dict):
    """测试用户注册"""
    # 发送注册请求
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": test_user["username"],
            "email": test_user["email"],
            "password": test_user["password"]
        },
    )
    
    # 验证响应状态码和返回数据
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["username"] == test_user["username"]
    assert "id" in data
    assert "hashed_password" not in data  # 密码哈希不应返回
    
    # 验证数据库中是否创建了用户
    user = db.query(User).filter(User.email == test_user["email"]).first()
    assert user is not None
    assert user.email == test_user["email"]
    assert user.username == test_user["username"]

# 测试重复注册
def test_register_existing_user(client, test_user: dict):
    """测试重复注册同一用户"""
    # 第一次注册
    client.post(
        "/api/v1/auth/register",
        json={
            "username": test_user["username"],
            "email": test_user["email"],
            "password": test_user["password"]
        },
    )
    
    # 尝试重复注册
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": test_user["username"],
            "email": test_user["email"],
            "password": test_user["password"]
        },
    )
    
    # 验证返回错误
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data
    assert "already registered" in data["detail"].lower()

# 测试用户登录
def test_login_user(client, db: Session, test_user: dict):
    """测试用户登录"""
    # 先创建用户
    user = User(
        email=test_user["email"],
        username=test_user["username"],
        hashed_password=get_password_hash(test_user["password"]),
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # 发送登录请求
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        },
    )
    
    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

# 测试使用错误密码登录
def test_login_incorrect_password(client, test_user: dict):
    """测试使用错误密码登录"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user["username"],
            "password": "wrongpassword"
        },
    )
    
    # 验证返回错误
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data
    assert "incorrect" in data["detail"].lower()

# 测试不存在的用户登录
def test_login_nonexistent_user(client):
    """测试不存在的用户登录"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent",
            "password": "password"
        },
    )
    
    # 验证返回错误
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data
    assert "incorrect" in data["detail"].lower()

# 测试非活跃用户登录
def test_login_inactive_user(client, db: Session, test_user: dict):
    """测试非活跃用户登录"""
    # 创建非活跃用户
    user = User(
        email=test_user["email"],
        username=test_user["username"],
        hashed_password=get_password_hash(test_user["password"]),
        is_active=False
    )
    db.add(user)
    db.commit()
    
    # 尝试登录
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        },
    )
    
    # 验证返回错误
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data
    assert "inactive" in data["detail"].lower()
