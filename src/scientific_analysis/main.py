"""
应用主入口 - 科学数据分析工具
负责初始化应用和启动主界面
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到系统路径，确保模块导入正常
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QStandardPaths

# 配置日志系统
logging.basicConfig(
    level=logging.INFO,  # 日志级别
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 日志格式
    handlers=[
        logging.StreamHandler(),  # 控制台输出
        logging.FileHandler(Path.home() / '.scientific_analysis' / 'app.log')  # 文件输出
    ]
)
logger = logging.getLogger(__name__)  # 获取日志记录器

# 导入应用组件
from ui.main_window import MainWindow  # 主窗口
from utils.resources import init_resources  # 资源初始化
from config import config  # 应用配置

def setup_application():
    """
    设置并启动应用程序
    1. 创建应用实例
    2. 初始化资源
    3. 设置应用元数据
    4. 显示主窗口
    5. 启动事件循环
    """
    # 创建Qt应用实例
    app = QApplication(sys.argv)
    
    # 初始化资源（图标、字体等）
    init_resources()
    
    # 设置应用元数据
    app.setApplicationName("科学分析工具")  # 应用名称
    app.setApplicationVersion("1.0.0")     # 版本号
    app.setOrganizationName("科学分析团队")  # 组织名称
    
    # 创建并显示主窗口
    main_window = MainWindow()
    main_window.show()
    
    # 启动应用事件循环
    sys.exit(app.exec())

if __name__ == "__main__":
    """应用入口点"""
    setup_application()