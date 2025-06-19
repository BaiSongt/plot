import logging
import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
project_root = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, project_root)

from alembic import command
from alembic.config import Config
from sqlalchemy_utils import create_database, database_exists

from app.core.config import settings
from app.db.session import engine, Base
from app.initial_data import init

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations() -> None:
    """运行数据库迁移"""
    logger.info("正在运行数据库迁移...")
    
    # 如果数据库不存在则创建
    if not database_exists(settings.DATABASE_URL):
        create_database(settings.DATABASE_URL)
        logger.info(f"已创建数据库: {settings.DATABASE_URL}")
    
    # 配置 Alembic
    alembic_cfg = Config("alembic.ini")
    
    # 运行迁移
    command.upgrade(alembic_cfg, "head")
    logger.info("数据库迁移完成")

def main() -> None:
    """初始化数据库并运行迁移"""
    try:
        # 运行迁移
        run_migrations()
        
        # 初始化数据
        init()
        
        logger.info("数据库初始化成功完成")
    except Exception as e:
        logger.error(f"初始化数据库时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
