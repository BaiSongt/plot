from datetime import timedelta, datetime
import time

import pytest
from jose import jwt
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_active_user,
    get_current_active_superuser,
    oauth2_scheme,
)
from app.core.config import settings
from app.models.user import User
from app.db.session import SessionLocal


def test_password_hashing():
    """测试密码哈希和验证"""
    # 测试密码哈希
    password = "testpass123"
    hashed_password = get_password_hash(password)
    
    # 验证密码
    assert verify_password(password, hashed_password) is True
    assert verify_password("wrongpassword", hashed_password) is False


def test_create_access_token():
    """测试创建访问令牌"""
    # 测试创建令牌
    data = {"sub": "testuser"}
    access_token = create_access_token(data)
    
    # 验证令牌格式
    assert isinstance(access_token, str)
    assert len(access_token.split(".")) == 3  # JWT 令牌应该有三个部分
    
    # 测试令牌过期
    expires_delta = timedelta(seconds=1)
    access_token = create_access_token(data, expires_delta=expires_delta)
    
    # 解码令牌
    payload = jwt.decode(
        access_token, 
        settings.APP_SECRET_KEY, 
        algorithms=[settings.ALGORITHM]
    )
    
    # 验证令牌内容
    assert payload["sub"] == "testuser"
    assert "exp" in payload
    
    # 验证令牌是否已过期
    time.sleep(2)  # 等待令牌过期
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(
            access_token, 
            settings.APP_SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )


def test_get_current_user(db):
    """测试获取当前用户"""
    # 创建测试用户
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 创建有效令牌
    access_token = create_access_token({"sub": user.username})
    
    # 模拟请求
    class MockRequest:
        def __init__(self, token: str):
            self.headers = {"Authorization": f"Bearer {token}"}
    
    # 获取当前用户
    current_user = get_current_user(
        db=db,
        token=access_token
    )
    
    # 验证用户
    assert current_user is not None
    assert current_user.username == user.username
    assert current_user.email == user.email
    
    # 测试无效令牌
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db=db, token="invalid.token.here")
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_active_user(db):
    """测试获取当前活跃用户"""
    # 创建活跃用户
    active_user = User(
        username="activeuser",
        email="active@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True
    )
    
    # 创建非活跃用户
    inactive_user = User(
        username="inactiveuser",
        email="inactive@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=False
    )
    
    db.add_all([active_user, inactive_user])
    db.commit()
    
    # 测试活跃用户
    current_active_user = get_current_active_user(active_user)
    assert current_active_user is active_user
    
    # 测试非活跃用户
    with pytest.raises(HTTPException) as exc_info:
        get_current_active_user(inactive_user)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Inactive user" in str(exc_info.value.detail)


def test_get_current_active_superuser(db):
    """测试获取当前超级用户"""
    # 创建超级用户
    superuser = User(
        username="superuser",
        email="super@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        is_superuser=True
    )
    
    # 创建普通用户
    normal_user = User(
        username="normaluser",
        email="normal@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        is_superuser=False
    )
    
    db.add_all([superuser, normal_user])
    db.commit()
    
    # 测试超级用户
    current_superuser = get_current_active_superuser(superuser)
    assert current_superuser is superuser
    
    # 测试普通用户
    with pytest.raises(HTTPException) as exc_info:
        get_current_active_superuser(normal_user)
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Not enough privileges" in str(exc_info.value.detail)


def test_oauth2_scheme():
    """测试 OAuth2 密码授权流"""
    # 创建测试表单数据
    form_data = OAuth2PasswordRequestForm(
        username="testuser",
        password="testpass123",
        scope="",
        client_id=None,
        client_secret=None
    )
    
    # 验证表单数据
    assert form_data.username == "testuser"
    assert form_data.password == "testpass123"
    assert form_data.scopes == []
    assert form_data.client_id is None
    assert form_data.client_secret is None
