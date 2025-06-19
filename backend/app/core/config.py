from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Any, Dict, Optional, Union
from pydantic import PostgresDsn, validator, field_validator
import secrets
import os
from pathlib import Path

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "Plot 数据可视化平台"
    APP_ENV: str = "development"
    APP_DEBUG: bool = False
    APP_SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # API 配置
    API_V1_STR: str = "/api/v1"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # 测试数据库配置
    TEST_DATABASE_URL: str = "sqlite:///./test.db"
    
    # 认证配置
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"
    
    # CORS 配置
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # 项目根目录
    PROJECT_ROOT: str = str(Path(__file__).parent.parent.parent)
    
    # 静态文件目录
    STATIC_DIR: str = os.path.join(PROJECT_ROOT, "static")
    
    # 上传文件配置
    UPLOAD_DIR: str = os.path.join(STATIC_DIR, "uploads")
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: List[str] = ["image/", "application/pdf", "text/plain"]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 开发环境专用配置
    FIRST_SUPERUSER: str = "admin"
    FIRST_SUPERUSER_PASSWORD: str = "changethis"
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return "sqlite:///./app.db"
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

# 创建配置实例
settings = Settings()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
