import os
import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
project_root = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, project_root)

from alembic.config import Config
from alembic import command

def make_migrations(message: str = "initial migration") -> None:
    """
    生成数据库迁移
    
    参数:
        message: 迁移描述信息
    """
    # 配置 Alembic
    alembic_cfg = Config("alembic.ini")
    
    # 生成迁移
    command.revision(
        config=alembic_cfg,
        autogenerate=True,
        message=message
    )
    print("迁移文件已生成，请检查并编辑生成的迁移文件。")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="生成数据库迁移")
    parser.add_argument(
        "-m", "--message", 
        type=str, 
        default="initial migration",
        help="迁移描述信息"
    )
    
    args = parser.parse_args()
    make_migrations(args.message)
