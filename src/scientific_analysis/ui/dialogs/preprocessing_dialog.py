# d:\works\plot\src\scientific_analysis\ui\dialogs\preprocessing_dialog.py
"""
Dialog for data preprocessing operations.
"""

from typing import Dict, List, Any, Optional, Union, Tuple

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
    QComboBox, QPushButton, QTabWidget, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QCheckBox,
    QDoubleSpinBox, QLineEdit, QFormLayout, QGroupBox,
    QSpinBox, QSplitter, QListWidget, QListWidgetItem,
    QAbstractItemView, QSizePolicy, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

import pandas as pd
import numpy as np

from scientific_analysis.data.preprocessing import (
    DataPreprocessor, MissingValueStrategy, DataType, NormalizationMethod
)
from scientific_analysis.utils.logger import get_logger

logger = get_logger(__name__)


class PreprocessingDialog(QDialog):
    """Dialog for performing data preprocessing operations."""
    
    preprocessingApplied = Signal(pd.DataFrame)
    
    def __init__(self, df: pd.DataFrame, parent=None):
        super().__init__(parent)
        self.original_df = df.copy()
        self.preprocessor = DataPreprocessor(df)
        self.current_df = df.copy()
        
        self.setWindowTitle("Data Preprocessing")
        self.setMinimumSize(1000, 700)
        
        self._init_ui()
        self._update_summary()
    
    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Create splitter for left/right panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - operations
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Tabs for different preprocessing operations
        self.tab_widget = QTabWidget()
        
        # Initialize tabs
        self._init_missing_values_tab()
        self._init_data_types_tab()
        self._init_normalization_tab()
        self._init_outliers_tab()
        self._init_filter_tab()
        
        left_layout.addWidget(self.tab_widget)
        
        # Preview/Apply buttons
        button_box = QDialogButtonBox()
        self.apply_btn = button_box.addButton("Apply", QDialogButtonBox.ApplyRole)
        self.reset_btn = button_box.addButton("Reset", QDialogButtonBox.ResetRole)
        self.close_btn = button_box.addButton("Close", QDialogButtonBox.RejectRole)
        
        self.apply_btn.clicked.connect(self._apply_preprocessing)
        self.reset_btn.clicked.connect(self._reset_preprocessing)
        self.close_btn.clicked.connect(self.reject)
        
        left_layout.addWidget(button_box)
        
        # Right panel - data preview and summary
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Summary group
        summary_group = QGroupBox("Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(2)
        self.summary_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.summary_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.summary_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.summary_table.verticalHeader().setVisible(False)
        self.summary_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        summary_layout.addWidget(self.summary_table)
        
        # Data preview
        preview_group = QGroupBox("Data Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_table = QTableWidget()
        self.preview_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        
        preview_layout.addWidget(self.preview_table)
        
        right_layout.addWidget(summary_group, 1)
        right_layout.addWidget(preview_group, 2)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 600])
        
        main_layout.addWidget(splitter)
    
    def _init_missing_values_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Strategy selection
        strategy_group = QGroupBox("Handling Strategy")
        strategy_layout = QFormLayout(strategy_group)
        
        self.missing_strategy_combo = QComboBox()
        for strategy in MissingValueStrategy:
            self.missing_strategy_combo.addItem(
                strategy.name.replace('_', ' ').title(),
                strategy
            )
        
        self.fill_value_edit = QLineEdit()
        self.fill_value_edit.setPlaceholderText("Enter fill value")
        self.fill_value_edit.setEnabled(False)
        
        self.missing_strategy_combo.currentIndexChanged.connect(
            lambda i: self.fill_value_edit.setEnabled(
                self.missing_strategy_combo.currentData() == MissingValueStrategy.FILL_VALUE
            )
        )
        
        strategy_layout.addRow("Strategy:", self.missing_strategy_combo)
        strategy_layout.addRow("Fill value:", self.fill_value_edit)
        
        # Columns selection
        columns_group = QGroupBox("Columns")
        columns_layout = QVBoxLayout(columns_group)
        
        self.missing_columns_list = QListWidget()
        self.missing_columns_list.setSelectionMode(QListWidget.MultiSelection)
        
        # Add columns with missing values
        missing_cols = self.original_df.columns[self.original_df.isna().any()].tolist()
        for col in self.original_df.columns:
            item = QListWidgetItem(col)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if col in missing_cols else Qt.Unchecked)
            self.missing_columns_list.addItem(item)
        
        columns_layout.addWidget(QLabel("Select columns to process:"))
        columns_layout.addWidget(self.missing_columns_list)
        
        layout.addWidget(strategy_group)
        layout.addWidget(columns_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Missing Values")
    
    def _init_data_types_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Data type conversion table
        type_group = QGroupBox("Data Type Conversion")
        type_layout = QVBoxLayout(type_group)
        
        self.dtype_table = QTableWidget()
        self.dtype_table.setColumnCount(2)
        self.dtype_table.setHorizontalHeaderLabels(["Column", "Data Type"])
        self.dtype_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.dtype_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.dtype_table.verticalHeader().setVisible(False)
        
        # Populate table
        self._update_dtype_table()
        
        type_layout.addWidget(self.dtype_table)
        
        layout.addWidget(type_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Data Types")
    
    def _init_normalization_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Method selection
        method_group = QGroupBox("Normalization Method")
        method_layout = QVBoxLayout(method_group)
        
        self.norm_method_combo = QComboBox()
        for method in NormalizationMethod:
            self.norm_method_combo.addItem(
                method.name.replace('_', ' ').title(),
                method
            )
        
        method_layout.addWidget(QLabel("Select normalization method:"))
        method_layout.addWidget(self.norm_method_combo)
        
        # Columns selection
        columns_group = QGroupBox("Columns")
        columns_layout = QVBoxLayout(columns_group)
        
        self.norm_columns_list = QListWidget()
        self.norm_columns_list.setSelectionMode(QListWidget.MultiSelection)
        
        # Add only numeric columns
        numeric_cols = self.original_df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            item = QListWidgetItem(col)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.norm_columns_list.addItem(item)
        
        columns_layout.addWidget(QLabel("Select numeric columns to normalize:"))
        columns_layout.addWidget(self.norm_columns_list)
        
        layout.addWidget(method_group)
        layout.addWidget(columns_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Normalization")
    
    def _init_outliers_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Detection method
        method_group = QGroupBox("Outlier Detection")
        method_layout = QFormLayout(method_group)
        
        self.outlier_method_combo = QComboBox()
        self.outlier_method_combo.addItem("Z-Score", 'zscore')
        self.outlier_method_combo.addItem("IQR (Interquartile Range)", 'iqr')
        
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(0.1, 10.0)
        self.threshold_spin.setValue(3.0)
        self.threshold_spin.setSingleStep(0.1)
        
        # Action selection
        self.outlier_action_combo = QComboBox()
        self.outlier_action_combo.addItem("Detect only", 'detect')
        self.outlier_action_combo.addItem("Remove outliers", 'remove')
        self.outlier_action_combo.addItem("Winsorize (cap values)", 'winsorize')
        
        method_layout.addRow("Method:", self.outlier_method_combo)
        method_layout.addRow("Threshold:", self.threshold_spin)
        method_layout.addRow("Action:", self.outlier_action_combo)
        
        # Columns selection
        columns_group = QGroupBox("Columns")
        columns_layout = QVBoxLayout(columns_group)
        
        self.outlier_columns_list = QListWidget()
        self.outlier_columns_list.setSelectionMode(QListWidget.MultiSelection)
        
        # Add only numeric columns
        numeric_cols = self.original_df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            item = QListWidgetItem(col)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.outlier_columns_list.addItem(item)
        
        columns_layout.addWidget(QLabel("Select numeric columns to analyze:"))
        columns_layout.addWidget(self.outlier_columns_list)
        
        layout.addWidget(method_group)
        layout.addWidget(columns_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Outliers")
    
    def _init_filter_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Filter expression
        filter_group = QGroupBox("Filter Rows")
        filter_layout = QVBoxLayout(filter_group)
        
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("e.g., age > 30 & income > 50000")
        
        filter_help = QLabel(
            "Enter a boolean expression to filter rows. "
            "Use column names as variables. Example: 'age > 30 & income > 50000'"
        )
        filter_help.setWordWrap(True)
        
        filter_layout.addWidget(QLabel("Filter expression:"))
        filter_layout.addWidget(self.filter_edit)
        filter_layout.addWidget(filter_help)
        
        layout.addWidget(filter_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Filter")
    
    def _update_dtype_table(self):
        """Update the data type conversion table with current column types."""
        self.dtype_table.setRowCount(len(self.current_df.columns))
        
        for i, col in enumerate(self.current_df.columns):
            # Column name
            col_item = QTableWidgetItem(col)
            self.dtype_table.setItem(i, 0, col_item)
            
            # Data type selector
            type_combo = QComboBox()
            for dtype in DataType:
                type_combo.addItem(dtype.name.replace('_', ' ').title(), dtype)
            
            # Set current type
            current_type = str(self.current_df[col].dtype)
            for j in range(type_combo.count()):
                if type_combo.itemData(j).name.lower() in current_type:
                    type_combo.setCurrentIndex(j)
                    break
            
            self.dtype_table.setCellWidget(i, 1, type_combo)
    
    def _update_summary(self):
        """Update the summary table and data preview."""
        # Summary table
        self.summary_table.setRowCount(5)
        
        # Row 0: Shape
        self.summary_table.setItem(0, 0, QTableWidgetItem("Shape"))
        self.summary_table.setItem(0, 1, QTableWidgetItem(f"{self.current_df.shape[0]} rows x {self.current_df.shape[1]} columns"))
        
        # Row 1: Missing values
        missing_total = self.current_df.isna().sum().sum()
        self.summary_table.setItem(1, 0, QTableWidgetItem("Missing Values"))
        self.summary_table.setItem(1, 1, QTableWidgetItem(str(missing_total)))
        
        # Row 2: Numeric columns
        numeric_cols = self.current_df.select_dtypes(include=['number']).columns
        self.summary_table.setItem(2, 0, QTableWidgetItem("Numeric Columns"))
        self.summary_table.setItem(2, 1, QTableWidgetItem(str(len(numeric_cols))))
        
        # Row 3: Categorical columns
        cat_cols = self.current_df.select_dtypes(include=['object', 'category']).columns
        self.summary_table.setItem(3, 0, QTableWidgetItem("Categorical Columns"))
        self.summary_table.setItem(3, 1, QTableWidgetItem(str(len(cat_cols))))
        
        # Row 4: Date columns
        date_cols = self.current_df.select_dtypes(include=['datetime']).columns
        self.summary_table.setItem(4, 0, QTableWidgetItem("Date Columns"))
        self.summary_table.setItem(4, 1, QTableWidgetItem(str(len(date_cols))))
        
        # Data preview
        self._update_preview()
    
    def _update_preview(self):
        """Update the data preview table."""
        preview_df = self.current_df.head(20)
        rows, cols = preview_df.shape
        
        self.preview_table.setRowCount(rows)
        self.preview_table.setColumnCount(cols)
        self.preview_table.setHorizontalHeaderLabels(preview_df.columns.tolist())
        
        for i in range(rows):
            for j in range(cols):
                value = preview_df.iat[i, j]
                if pd.isna(value):
                    item = QTableWidgetItem("NaN")
                    item.setBackground(Qt.lightGray)
                else:
                    item = QTableWidgetItem(str(value))
                self.preview_table.setItem(i, j, item)
        
        self.preview_table.resizeColumnsToContents()
    
    def _apply_preprocessing(self):
        """Apply all preprocessing operations."""
        try:
            # Apply missing values handling
            strategy = self.missing_strategy_combo.currentData()
            fill_value = self.fill_value_edit.text() if strategy == MissingValueStrategy.FILL_VALUE else None
            
            # Get selected columns
            selected_columns = []
            for i in range(self.missing_columns_list.count()):
                item = self.missing_columns_list.item(i)
                if item.checkState() == Qt.Checked:
                    selected_columns.append(item.text())
            
            if selected_columns:
                self.preprocessor.handle_missing_values(
                    strategy=strategy,
                    columns=selected_columns,
                    fill_value=fill_value
                )
            
            # Apply data type conversion
            for i in range(self.dtype_table.rowCount()):
                col = self.dtype_table.item(i, 0).text()
                combo = self.dtype_table.cellWidget(i, 1)
                dtype = combo.currentData()
                
                self.preprocessor.convert_dtypes({col: dtype})
            
            # Apply normalization
            norm_method = self.norm_method_combo.currentData()
            norm_columns = []
            for i in range(self.norm_columns_list.count()):
                item = self.norm_columns_list.item(i)
                if item.checkState() == Qt.Checked:
                    norm_columns.append(item.text())
            
            if norm_columns:
                self.preprocessor.normalize(
                    method=norm_method,
                    columns=norm_columns
                )
            
            # Apply outlier handling
            outlier_method = self.outlier_method_combo.currentData()
            outlier_action = self.outlier_action_combo.currentData()
            threshold = self.threshold_spin.value()
            outlier_columns = []
            for i in range(self.outlier_columns_list.count()):
                item = self.outlier_columns_list.item(i)
                if item.checkState() == Qt.Checked:
                    outlier_columns.append(item.text())
            
            if outlier_columns:
                self.preprocessor.handle_outliers(
                    method=outlier_method,
                    action=outlier_action,
                    threshold=threshold,
                    columns=outlier_columns
                )
            
            # Apply filter
            filter_expr = self.filter_edit.text().strip()
            if filter_expr:
                self.preprocessor.filter_rows(filter_expr)
            
            # Get processed data
            self.current_df = self.preprocessor.get_processed_data()
            
            # Update UI
            self._update_summary()
            
            QMessageBox.information(self, "Success", "Preprocessing applied successfully!")
            
        except Exception as e:
            logger.error(f"Error applying preprocessing: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to apply preprocessing:\n{str(e)}")
    
    def _reset_preprocessing(self):
        """Reset to original data."""
        self.preprocessor = DataPreprocessor(self.original_df)
        self.current_df = self.original_df.copy()
        self._update_summary()
        QMessageBox.information(self, "Reset", "Preprocessing reset to original data.")
    
    def get_processed_data(self) -> pd.DataFrame:
        """Return the processed DataFrame."""
        return self.current_df