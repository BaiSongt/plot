"""
Main application window for the Scientific Analysis Tool.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QSplitter, QTreeWidget, QTreeWidgetItem,
    QTextEdit, QLabel, QFrame, QMenuBar, QStatusBar,
    QMessageBox, QPushButton, QDialog, QFormLayout, QLineEdit
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QAction, QIcon

from ..data.manager import DataManager
from ..config.settings import Settings
from ..config.config_manager import get_config_manager
from ..integration.web_view import EmbeddedWebWidget
from .login_dialog import LoginDialog
from ..integration.api_client import APIClient

from scientific_analysis.data.preprocessing import (  # 使用绝对路径导入
    DataPreprocessor, MissingValueStrategy, DataType, NormalizationMethod
)

class MainWindow(QMainWindow):
    """主窗口类"""
    
    # 信号
    data_updated = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize managers and clients
        self.data_manager = DataManager()
        self.settings = Settings()
        self.config_manager = get_config_manager()
        
        # Initialize API client with backend URL from config
        backend_url = self.config_manager.get_backend_url()
        self.api_client = APIClient(base_url=backend_url)
        
        # Set window properties
        self.setWindowTitle("科学数据分析工具")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Center the window on screen
        self.center_on_screen()
        
        # Initialize UI components
        self._create_actions()
        self._create_menu_bar()
        self._create_status_bar()
        self._create_dock_widgets()
        self._create_central_widget()
        self.setup_api_connection()
        
        # Initialize application state
        self.current_file = None
        self.current_dataset = None
        
        # Apply settings
        self.apply_settings()
    
    def _create_actions(self):
        """Create menu actions."""
        # File menu actions
        self.new_action = QAction("新建(&N)", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self.new_file)
        
        self.open_action = QAction("打开(&O)...", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.open_file)
        
        self.save_action = QAction("保存(&S)", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_file)
        
        self.save_as_action = QAction("另存为(&A)...", self)
        self.save_as_action.triggered.connect(self.save_file_as)
        
        self.exit_action = QAction("退出(&X)", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)
        
        # Help menu actions
        self.about_action = QAction("关于(&A)", self)
        self.about_action.triggered.connect(self.show_about)
    
    def _create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("文件(&F)")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("编辑(&E)")
        # Add edit actions here
        
        # View menu
        view_menu = menubar.addMenu("视图(&V)")
        # Add view actions here
        
        # Data menu
        data_menu = menubar.addMenu("数据(&D)")
        # Create data preprocessing action
        self.preprocess_action = QAction("数据预处理(&P)", self)
        self.preprocess_action.triggered.connect(self.open_preprocessing_dialog)
        data_menu.addAction(self.preprocess_action)
        data_menu.addSeparator()
        
        # 添加数据同步功能
        sync_to_backend_action = QAction("同步到后端(&U)", self)
        sync_to_backend_action.triggered.connect(self.sync_data_to_backend)
        data_menu.addAction(sync_to_backend_action)
        
        sync_from_backend_action = QAction("从后端同步(&D)", self)
        sync_from_backend_action.triggered.connect(self.sync_data_from_backend)
        data_menu.addAction(sync_from_backend_action)
        
        data_menu.addSeparator()
        
        # 添加登录功能
        login_action = QAction("登录后端(&L)", self)
        login_action.triggered.connect(self.show_login_dialog)
        data_menu.addAction(login_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("工具(&T)")
        # Add tools actions here
        
        # Help menu
        help_menu = menubar.addMenu("帮助(&H)")
        help_menu.addAction(self.about_action)
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.statusBar().showMessage("Ready")
    
    def _create_dock_widgets(self):
        """Create dock widgets."""
        from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QLabel, QScrollArea
        
        # Left dock for data explorer
        self.data_dock = QDockWidget("数据浏览器", self)
        self.data_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        # Create data explorer content
        data_explorer = QTreeWidget()
        data_explorer.setHeaderLabel("数据集")
        
        # Add sample items
        root_item = QTreeWidgetItem(data_explorer, ["当前数据集"])
        columns_item = QTreeWidgetItem(root_item, ["列信息"])
        stats_item = QTreeWidgetItem(root_item, ["统计信息"])
        
        self.data_dock.setWidget(data_explorer)
        self.data_dock.setMinimumWidth(250)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.data_dock)
        
        # Right dock for properties/options
        self.properties_dock = QDockWidget("属性面板", self)
        self.properties_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        # Create properties content
        properties_widget = QWidget()
        properties_layout = QVBoxLayout(properties_widget)
        properties_layout.addWidget(QLabel("图表属性"))
        properties_layout.addWidget(QLabel("分析参数"))
        properties_layout.addWidget(QLabel("导出选项"))
        properties_layout.addStretch()
        
        self.properties_dock.setWidget(properties_widget)
        self.properties_dock.setMinimumWidth(200)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)
    
    def _create_central_widget(self):
        """Create the central widget with tabs."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.visualization_tab = self.create_visualization_tab()
        self.analysis_tab = self.create_analysis_tab()
        self.web_tab = EmbeddedWebWidget()
        
        self.tab_widget.addTab(self.visualization_tab, "可视化(&V)")
        self.tab_widget.addTab(self.analysis_tab, "分析(&A)")
        self.tab_widget.addTab(self.web_tab, "Web界面(&W)")
        
        layout.addWidget(self.tab_widget)
        
        # 连接Web视图信号
        self.web_tab.get_web_view().connection_changed.connect(self.on_web_connection_changed)
    
    def center_on_screen(self):
        """Center the window on the screen."""
        from PySide6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().geometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
    
    # Slots
    def new_file(self):
        """Create a new file."""
        # TODO: Implement new file creation
        self.statusBar().showMessage("Creating new file...", 2000)
    
    def open_file(self):
        """Open a file."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*);;CSV Files (*.csv);;Excel Files (*.xlsx);;JSON Files (*.json)"
        )
        
        if file_name:
            # TODO: Implement file loading
            self.current_file = file_name
            self.statusBar().showMessage(f"Opened: {file_name}", 2000)
    
    def save_file(self):
        """Save the current file."""
        if self.current_file:
            # TODO: Implement file saving
            self.statusBar().showMessage(f"Saved: {self.current_file}", 2000)
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """Save the current file with a new name."""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",
            "All Files (*);;CSV Files (*.csv);;Excel Files (*.xlsx);;JSON Files (*.json)"
        )
        
        if file_name:
            self.current_file = file_name
            # TODO: Implement file saving
            self.statusBar().showMessage(f"Saved as: {file_name}", 2000)
    
    def create_visualization_tab(self):
        """创建可视化选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 添加可视化控件
        label = QLabel("数据可视化面板")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        # 这里可以添加具体的可视化组件
        
        return widget
    
    def create_analysis_tab(self):
        """创建分析选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 添加分析控件
        label = QLabel("数据分析面板")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        # 这里可以添加具体的分析组件
        
        return widget
    
    def setup_api_connection(self):
        """设置API连接"""
        # 检查API连接状态
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self.check_api_connection)
        self.connection_timer.start(10000)  # 每10秒检查一次
        
        # 立即检查一次
        self.check_api_connection()
    
    def check_api_connection(self):
        """检查API连接状态"""
        if self.api_client.is_connected():
            self.statusBar().showMessage("后端服务已连接", 2000)
        else:
            self.statusBar().showMessage("后端服务未连接", 2000)
    
    def on_web_connection_changed(self, connected: bool):
        """Web连接状态改变"""
        if connected:
            self.statusBar().showMessage("Web服务连接成功", 3000)
        else:
            self.statusBar().showMessage("Web服务连接失败", 3000)
    
    def sync_data_to_backend(self):
        """同步数据到后端"""
        if not self.api_client.is_connected():
            QMessageBox.warning(self, "警告", "后端服务未连接，无法同步数据")
            return
        
        # 获取本地数据
        local_data = {
            'datasets': self.data_manager.get_all_datasets(),
            'visualizations': []  # 这里可以添加可视化配置
        }
        
        # 同步到后端
        success = self.api_client.sync_data_to_backend(local_data)
        if success:
            QMessageBox.information(self, "成功", "数据同步到后端成功")
        else:
            QMessageBox.warning(self, "失败", "数据同步到后端失败")
    
    def sync_data_from_backend(self):
        """从后端同步数据"""
        if not self.api_client.is_connected():
            QMessageBox.warning(self, "警告", "后端服务未连接，无法同步数据")
            return
        
        # 从后端获取数据
        synced_data = self.api_client.sync_data_from_backend()
        
        # 更新本地数据
        for name, dataset in synced_data['datasets'].items():
            self.data_manager.add_dataset(name, dataset)
        
        # 发出数据更新信号
        self.data_updated.emit()
        
        QMessageBox.information(self, "成功", f"从后端同步了 {len(synced_data['datasets'])} 个数据集")
    
    def show_login_dialog(self):
        """显示登录对话框"""
        backend_url = self.config_manager.get_backend_url()
        dialog = LoginDialog(self, base_url=backend_url)
        if dialog.exec() == QDialog.Accepted:
            user_info = dialog.get_user_info()
            if user_info:
                # 更新API客户端的认证信息
                self.api_client.set_auth_token(user_info.get('access_token'))
                self.statusBar().showMessage(f"已登录: {user_info.get('username', '未知用户')}", 5000)
                
                # 更新配置中的后端URL（如果用户修改了）
                new_backend_url = dialog.get_base_url()
                if new_backend_url != backend_url:
                    self.config_manager.set_backend_url(new_backend_url)
                    self.api_client.base_url = new_backend_url
                
                # 同步数据
                self.sync_data_from_backend()
    
    def apply_settings(self):
        """应用设置"""
        # 这里可以应用用户设置
        pass
    
    def close_tab(self, index):
        """Close a tab."""
        if self.tab_widget.count() > 1:  # Keep at least one tab open
            self.tab_widget.removeTab(index)
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Scientific Analysis Tool",
            "<h2>Scientific Analysis Tool</h2>"
            "<p>Version 0.1.0</p>"
            "<p>A scientific computing and visualization tool built with PySide6.</p>"
            "<p>© 2025 Scientific Analysis Tool Team</p>"
        )

    def open_preprocessing_dialog(self):
        """Open the preprocessing dialog."""
        if not self.current_dataset:
            QMessageBox.warning(self, "Warning", "No dataset loaded!")
            return
        
        dialog = PreprocessingDialog(self.current_dataset.data, self)
        if dialog.exec() == QDialog.Accepted:
            processed_df = dialog.get_processed_data()
            # Update your dataset with the processed data
            self.current_dataset.data = processed_df
            self.update_data_view()