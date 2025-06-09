"""
Main application window for the Scientific Analysis Tool.
"""

from PySide6.QtWidgets import (
    QMainWindow, QDockWidget, QWidget, QVBoxLayout, 
    QTabWidget, QStatusBar, QMenuBar, QMenu, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon

from scientific_analysis.data.preprocessing import (  # 使用绝对路径导入
    DataPreprocessor, MissingValueStrategy, DataType, NormalizationMethod
)

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set window properties
        self.setWindowTitle("Scientific Analysis Tool")
        self.setMinimumSize(1024, 768)
        
        # Initialize UI components
        self._create_actions()
        self._create_menu_bar()
        self._create_status_bar()
        self._create_dock_widgets()
        self._create_central_widget()
        
        # Initialize application state
        self.current_file = None
    
    def _create_actions(self):
        """Create menu actions."""
        # File menu actions
        self.new_action = QAction("&New", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self.new_file)
        
        self.open_action = QAction("&Open...", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.open_file)
        
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_file)
        
        self.save_as_action = QAction("Save &As...", self)
        self.save_as_action.triggered.connect(self.save_file_as)
        
        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)
        
        # Help menu actions
        self.about_action = QAction("&About", self)
        self.about_action.triggered.connect(self.show_about)
    
    def _create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        # Add edit actions here
        
        # View menu
        view_menu = menubar.addMenu("&View")
        # Add view actions here
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        # Add tools actions here
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction(self.about_action)
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.statusBar().showMessage("Ready")
    
    def _create_dock_widgets(self):
        """Create dock widgets."""
        # Left dock for data explorer
        self.data_dock = QDockWidget("Data Explorer", self)
        self.data_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.data_dock)
        
        # Right dock for properties/options
        self.properties_dock = QDockWidget("Properties", self)
        self.properties_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
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
        
        layout.addWidget(self.tab_widget)
    
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