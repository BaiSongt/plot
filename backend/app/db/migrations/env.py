from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

# 导入应用配置和模型
from app.core.config import settings
from app.db.base import Base

# 这是 Alembic 配置对象，提供对 .ini 文件中的值的访问。
config = context.config

# 设置 SQLAlchemy URL
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """在 'offline' 模式下运行迁移。

    这配置了带有 URL 的上下文，并且不需要 DBAPI 可用。
    通过调用 context.execute() 来发出对 context 的语句。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """在 'online' 模式下运行迁移。

    在这种情况下，我们创建了一个 Engine 并将其与连接关联。
    """
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
