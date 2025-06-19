import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User

# 测试获取当前用户
def test_get_current_user(client: TestClient, db: Session, test_user: dict):
    """测试获取当前用户信息"""
    # 创建测试用户
    user = User(
        email=test_user["email"],
        username=test_user["username"],
        hashed_password=get_password_hash(test_user["password"]),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 登录获取token
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"],
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    tokens = response.json()
    access_token = tokens["access_token"]
    
    # 获取当前用户信息
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["username"] == test_user["username"]
    assert "id" in data
    assert "hashed_password" not in data

# 测试未认证用户访问受保护端点
def test_unauthorized_access(client: TestClient):
    """测试未认证用户访问受保护端点"""
    response = client.get("/api/v1/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# 测试更新用户信息
def test_update_user(client: TestClient, db: Session, test_user: dict):
    """测试更新用户信息"""
    # 创建测试用户
    user = User(
        email=test_user["email"],
        username=test_user["username"],
        hashed_password=get_password_hash(test_user["password"]),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 登录获取token
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"],
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    tokens = response.json()
    access_token = tokens["access_token"]
    
    # 更新用户信息
    update_data = {
        "email": "updated@example.com",
        "username": "updated_username"
    }
    
    response = client.put(
        f"/api/v1/users/{user.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == update_data["email"]
    assert data["username"] == update_data["username"]
    
    # 验证数据库中的更新
    db_user = db.query(User).filter(User.id == user.id).first()
    assert db_user is not None
    assert db_user.email == update_data["email"]
    assert db_user.username == update_data["username"]

# 测试删除用户
def test_delete_user(client: TestClient, db: Session, test_user: dict):
    """测试删除用户"""
    # 创建测试用户
    user = User(
        email=test_user["email"],
        username=test_user["username"],
        hashed_password=get_password_hash(test_user["password"]),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 登录获取token
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"],
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    tokens = response.json()
    access_token = tokens["access_token"]
    
    # 删除用户
    response = client.delete(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == user.id
    assert data["email"] == user.email
    
    # 验证用户已被删除
    db_user = db.query(User).filter(User.id == user.id).first()
    assert db_user is None

# 测试更新其他用户信息（非管理员）
def test_update_other_user(client: TestClient, db: Session, test_user: dict):
    """测试普通用户尝试更新其他用户信息"""
    # 创建测试用户1
    user1 = User(
        email=test_user["email"],
        username=test_user["username"],
        hashed_password=get_password_hash(test_user["password"]),
        is_active=True
    )
    db.add(user1)
    db.commit()
    db.refresh(user1)
    
    # 创建测试用户2
    user2 = User(
        email="another@example.com",
        username="anotheruser",
        hashed_password=get_password_hash("anotherpassword"),
        is_active=True
    )
    db.add(user2)
    db.commit()
    db.refresh(user2)
    
    # 用户1登录
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"],
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    tokens = response.json()
    access_token = tokens["access_token"]
    
    # 用户1尝试更新用户2的信息
    update_data = {
        "email": "hacked@example.com"
    }
    
    response = client.put(
        f"/api/v1/users/{user2.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    # 验证返回403禁止访问
    assert response.status_code == status.HTTP_403_FORBIDDEN
