import pytest
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import get_password_hash

def test_user_model(db: Session):
    """测试用户模型"""
    # 创建测试用户
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        is_superuser=False,
    )
    
    # 添加到数据库
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 验证用户属性
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True
    assert user.is_superuser is False
    assert hasattr(user, "id")
    assert hasattr(user, "created_at")
    assert hasattr(user, "updated_at")
    
    # 测试密码验证
    assert user.verify_password("testpass123") is True
    assert user.verify_password("wrongpassword") is False

def test_user_to_dict(db: Session):
    """测试用户模型的 to_dict 方法"""
    # 创建测试用户
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 转换为字典
    user_dict = user.to_dict()
    
    # 验证字典内容
    assert user_dict["username"] == "testuser"
    assert user_dict["email"] == "test@example.com"
    assert "id" in user_dict
    assert "created_at" in user_dict
    assert "updated_at" in user_dict
    assert "hashed_password" not in user_dict  # 密码哈希不应包含在字典中

def test_user_update(db: Session):
    """测试用户模型的 update 方法"""
    # 创建测试用户
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 更新用户信息
    user.update(
        username="updateduser",
        email="updated@example.com"
    )
    db.commit()
    db.refresh(user)
    
    # 验证更新后的信息
    assert user.username == "updateduser"
    assert user.email == "updated@example.com"
    
    # 验证不能更新 id、created_at 和 updated_at
    original_created_at = user.created_at
    original_updated_at = user.updated_at
    
    user.update(
        id=999,  # 应该被忽略
        created_at=None,  # 应该被忽略
        updated_at=None  # 应该被忽略
    )
    db.commit()
    db.refresh(user)
    
    assert user.id != 999
    assert user.created_at == original_created_at
    assert user.updated_at != original_updated_at  # updated_at 应该自动更新

def test_user_token_generation():
    """测试用户令牌生成和验证"""
    from datetime import timedelta
    from app.core.config import settings
    
    # 创建测试用户
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
    )
    
    # 生成访问令牌
    access_token = user.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # 验证令牌
    payload = user.verify_token(access_token)
    assert payload is not None
    assert payload["sub"] == user.username
    
    # 验证无效令牌
    invalid_token = "invalid.token.here"
    assert user.verify_token(invalid_token) is None

@pytest.mark.parametrize("username,email,password,is_valid", [
    ("validuser", "valid@example.com", "ValidPass123", True),
    ("", "valid@example.com", "ValidPass123", False),  # 空的用户名
    ("validuser", "invalid-email", "ValidPass123", False),  # 无效的邮箱
    ("validuser", "valid@example.com", "short", False),  # 密码太短
])
def test_user_validation(db: Session, username: str, email: str, password: str, is_valid: bool):
    """测试用户模型验证"""
    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
    )
    
    if is_valid:
        db.add(user)
        db.commit()
        db.refresh(user)
        assert user.id is not None
    else:
        with pytest.raises(Exception):
            db.add(user)
            db.commit()
        db.rollback()
