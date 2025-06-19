"""
Main application window for the Scientific Analysis Tool.
"""

from PySide6.QtWidgets import (
    QMainWindow, QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTabWidget, QStatusBar, QMenuBar, QMenu, QToolBar, QFileDialog, QMessageBox, QDialog
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon

from .dialogs.preprocessing_dialog import PreprocessingDialog
from .visualization_panel import VisualizationPanel
from .analysis_panel import AnalysisPanel
from scientific_analysis.data.manager import DataManager

from scientific_analysis.data.preprocessing import (  # 使用绝对路径导入
    DataPreprocessor, MissingValueStrategy, DataType, NormalizationMethod
)

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set window properties
        self.setWindowTitle("科学数据分析工具")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Center the window on screen
        self.center_on_screen()
        
        # Initialize data manager
        self.data_manager = DataManager()
        
        # Initialize UI components
        self._create_actions()
        self._create_menu_bar()
        self._create_status_bar()
        self._create_dock_widgets()
        self._create_central_widget()
        
        # Initialize application state
        self.current_file = None
        self.current_dataset = None
    
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
        """Create the central widget."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget for multiple documents/views
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        # Create visualization panel
        self.visualization_panel = VisualizationPanel(self.data_manager)
        self.tab_widget.addTab(self.visualization_panel, "数据可视化")
        
        # Create analysis panel
        self.analysis_panel = AnalysisPanel(self.data_manager)
        self.tab_widget.addTab(self.analysis_panel, "数据分析")
        
        layout.addWidget(self.tab_widget)
    
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
    
    def close_tab(self, index):
        """Close a tab."""
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