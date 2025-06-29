from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    获取数据库会话
    使用示例:
    ```
    db = next(get_db())
    ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
