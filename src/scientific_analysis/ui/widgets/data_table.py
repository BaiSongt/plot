"""
Data table view widget for displaying and editing tabular data.
"""

from typing import Any, Dict, List, Optional, Union, Tuple

import pandas as pd
import numpy as np
from PySide6.QtCore import (
    QAbstractTableModel, 
    QModelIndex, 
    Qt, 
    QSortFilterProxyModel,
    Signal,
    Slot,
    QItemSelection
)
from PySide6.QtGui import (
    QAction,
    QClipboard,
    QKeySequence,
    QKeyEvent
)
from PySide6.QtWidgets import (
    QApplication,
    QTableView,
    QMenu,
    QHeaderView,
    QAbstractItemView,
    QMessageBox
)

from ...models.dataset import Dataset


class PandasTableModel(QAbstractTableModel):
    """A model to interface a Qt view with pandas DataFrame."""
    
    def __init__(self, data: pd.DataFrame = None, parent=None):
        """Initialize the model with a pandas DataFrame.
        
        Args:
            data: The pandas DataFrame to display.
            parent: The parent widget.
        """
        super().__init__(parent)
        self._data = data if data is not None else pd.DataFrame()
        self._editable_columns = set()
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return the number of rows in the model."""
        if parent.isValid():
            return 0
        return len(self._data)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Return the number of columns in the model."""
        if parent.isValid():
            return 0
        return len(self._data.columns)
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Return the data for the given role and index."""
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return None
        
        if role == Qt.DisplayRole or role == Qt.EditRole:
            value = self._data.iat[index.row(), index.column()]
            
            # Convert numpy types to Python native types for display
            if pd.isna(value):
                return ""
            elif isinstance(value, (np.integer, np.floating)):
                return value.item()
            elif isinstance(value, (np.bool_)):
                return bool(value)
            return value
            
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        """Return the header data for the given section and orientation."""
        if role != Qt.DisplayRole:
            return None
            
        if orientation == Qt.Horizontal:
            return str(self._data.columns[section])
        else:
            return str(section + 1)  # 1-based row numbers
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Return the item flags for the given index."""
        if not index.isValid():
            return Qt.NoItemFlags
            
        flags = super().flags(index)
        
        # Make all cells selectable and enabled
        flags |= Qt.ItemIsSelectable | Qt.ItemIsEnabled
        
        # Make cells editable if the column is marked as editable
        if index.column() in self._editable_columns:
            flags |= Qt.ItemIsEditable
            
        return flags
    
    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        """Set the data at the given index to the given value."""
        if not index.isValid() or role != Qt.EditRole:
            return False
            
        try:
            # Get the current value and type
            current_value = self._data.iat[index.row(), index.column()]
            
            # Convert the input value to the correct type
            if pd.api.types.is_numeric_dtype(self._data.iloc[:, index.column()]):
                if pd.isna(current_value) or str(current_value).strip() == '':
                    # If current value is NA, try to infer the type from the column
                    try:
                        value = float(value)
                        if self._data.iloc[:, index.column()].dtype.kind in 'iu':
                            value = int(float(value))
                    except (ValueError, TypeError):
                        pass
                else:
                    # Otherwise, try to convert to the same type as the current value
                    try:
                        if isinstance(current_value, (int, np.integer)):
                            value = int(float(value))
                        elif isinstance(current_value, (float, np.floating)):
                            value = float(value)
                    except (ValueError, TypeError):
                        return False
            
            # Set the new value
            self._data.iat[index.row(), index.column()] = value
            
            # Emit dataChanged signal
            self.dataChanged.emit(index, index, [role])
            return True
            
        except Exception as e:
            print(f"Error setting data: {e}")
            return False
    
    def set_editable_columns(self, columns: List[Union[int, str]]) -> None:
        """Set which columns are editable.
        
        Args:
            columns: List of column indices or names to make editable.
        """
        self._editable_columns.clear()
        
        for col in columns:
            if isinstance(col, str) and col in self._data.columns:
                col_idx = self._data.columns.get_loc(col)
                self._editable_columns.add(col_idx)
            elif isinstance(col, int) and 0 <= col < len(self._data.columns):
                self._editable_columns.add(col)
        
        self.layoutChanged.emit()
    
    def set_dataframe(self, data: pd.DataFrame) -> None:
        """Set a new DataFrame for the model.
        
        Args:
            data: The new pandas DataFrame.
        """
        self.beginResetModel()
        self._data = data.copy()
        self.endResetModel()


class DataTableView(QTableView):
    """A table view widget for displaying and editing tabular data with pandas DataFrame."""
    
    # Signals
    dataChanged = Signal()
    selectionChanged = Signal(object)  # Emits the current selection
    
    def __init__(self, parent=None):
        """Initialize the data table view."""
        super().__init__(parent)
        
        # Set up the model and proxy model
        self._model = PandasTableModel()
        self._proxy_model = QSortFilterProxyModel(self)
        self._proxy_model.setSourceModel(self._model)
        self.setModel(self._proxy_model)
        
        # Configure view properties
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Set up headers
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)
        
        # Connect signals
        self.doubleClicked.connect(self._on_double_clicked)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.selectionModel().selectionChanged.connect(self._on_selection_changed)
        
        # Initialize context menu actions
        self._init_actions()
    
    def _init_actions(self) -> None:
        """Initialize context menu actions."""
        # Copy action
        self.copy_action = QAction("Copy", self)
        self.copy_action.setShortcut(QKeySequence.Copy)
        self.copy_action.triggered.connect(self.copy_selection)
        
        # Paste action
        self.paste_action = QAction("Paste", self)
        self.paste_action.setShortcut(QKeySequence.Paste)
        self.paste_action.triggered.connect(self.paste_data)
        
        # Delete action
        self.delete_action = QAction("Delete", self)
        self.delete_action.setShortcut(QKeySequence.Delete)
        self.delete_action.triggered.connect(self.delete_selected)
        
        # Add actions to the widget
        self.addAction(self.copy_action)
        self.addAction(self.paste_action)
        self.addAction(self.delete_action)
    
    def set_dataframe(self, data: pd.DataFrame) -> None:
        """Set the DataFrame to display in the view.
        
        Args:
            data: The pandas DataFrame to display.
        """
        self._model.set_dataframe(data)
        self.resize_columns_to_contents()
    
    def get_dataframe(self) -> pd.DataFrame:
        """Get the current DataFrame from the model.
        
        Returns:
            The current pandas DataFrame.
        """
        return self._model._data.copy()
    
    def resize_columns_to_contents(self) -> None:
        """Resize all columns to fit their contents."""
        self.resizeColumnsToContents()
    
    def set_editable_columns(self, columns: List[Union[int, str]]) -> None:
        """Set which columns are editable.
        
        Args:
            columns: List of column indices or names to make editable.
        """
        self._model.set_editable_columns(columns)
    
    def copy_selection(self) -> None:
        """Copy the current selection to the clipboard."""
        selection = self.selectionModel().selection()
        if not selection.isEmpty():
            # Get the selected indexes from the proxy model
            proxy_indexes = selection.indexes()
            
            # Map to source indexes
            source_indexes = [self._proxy_model.mapToSource(idx) for idx in proxy_indexes]
            
            if not source_indexes:
                return
                
            # Get row and column ranges
            rows = sorted({idx.row() for idx in source_indexes})
            cols = sorted({idx.column() for idx in source_indexes})
            
            # Get the data
            data = []
            for row in rows:
                row_data = []
                for col in cols:
                    idx = source_indexes[0].sibling(row, col)
                    item_data = self._model.data(idx, Qt.DisplayRole)
                    row_data.append(str(item_data) if item_data is not None else "")
                data.append("\t".join(row_data))
            
            # Join rows with newlines and set to clipboard
            clipboard = QApplication.clipboard()
            clipboard.setText("\n".join(data))
    
    def paste_data(self) -> None:
        """Paste data from clipboard into the table."""
        if not self._model._data.size or not self.selectionModel().hasSelection():
            return
            
        # Get the top-left cell of the selection
        selected_indexes = self.selectionModel().selectedIndexes()
        if not selected_indexes:
            return
            
        top_left = min(selected_indexes, key=lambda idx: (idx.row(), idx.column()))
        start_row = top_left.row()
        start_col = top_left.column()
        
        # Get clipboard data
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if not text:
            return
        
        # Parse the clipboard data
        rows = []
        for line in text.split('\n'):
            rows.append(line.split('\t') if '\t' in line else [line])
        
        # Update the model
        self._model.beginResetModel()
        
        try:
            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    current_row = start_row + i
                    current_col = start_col + j
                    
                    # Check if we're within bounds
                    if (current_row < self._model.rowCount() and 
                        current_col < self._model.columnCount()):
                        index = self._model.index(current_row, current_col)
                        self._model.setData(index, value, Qt.EditRole)
        finally:
            self._model.endResetModel()
        
        self.dataChanged.emit()
    
    def delete_selected(self) -> None:
        """Delete the selected cells."""
        if not self._model._data.size or not self.selectionModel().hasSelection():
            return
        
        # Get selected indexes from the proxy model
        proxy_indexes = self.selectionModel().selectedIndexes()
        if not proxy_indexes:
            return
        
        # Map to source indexes
        source_indexes = [self._proxy_model.mapToSource(idx) for idx in proxy_indexes]
        
        # Update the model
        self._model.beginResetModel()
        
        try:
            for index in source_indexes:
                if index.isValid():
                    self._model.setData(index, "", Qt.EditRole)
        finally:
            self._model.endResetModel()
        
        self.dataChanged.emit()
    
    def _show_context_menu(self, position) -> None:
        """Show the context menu at the given position."""
        menu = QMenu(self)
        menu.addAction(self.copy_action)
        menu.addAction(self.paste_action)
        menu.addSeparator()
        menu.addAction(self.delete_action)
        
        # Show the context menu
        menu.exec_(self.viewport().mapToGlobal(position))
    
    def _on_double_clicked(self, index: QModelIndex) -> None:
        """Handle double-click events on cells."""
        if index.isValid():
            self.edit(index)
    
    def _on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        """Handle selection changes."""
        # Emit the current selection
        indexes = self.selectionModel().selectedIndexes()
        if indexes:
            # Get unique rows and columns
            rows = sorted({idx.row() for idx in indexes})
            cols = sorted({idx.column() for idx in indexes})
            
            # Get the data
            data = []
            for row in rows:
                row_data = []
                for col in cols:
                    idx = indexes[0].sibling(row, col)
                    item_data = self._model.data(idx, Qt.DisplayRole)
                    row_data.append(str(item_data) if item_data is not None else "")
                data.append(row_data)
            
            self.selectionChanged.emit({
                'rows': rows,
                'columns': cols,
                'data': data
            })
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press events."""
        # Handle Ctrl+C for copy
        if event.matches(QKeySequence.Copy):
            self.copy_selection()
            return
            
        # Handle Ctrl+V for paste
        if event.matches(QKeySequence.Paste):
            self.paste_data()
            return
            
        # Handle Delete key
        if event.key() == Qt.Key_Delete:
            self.delete_selected()
            return
            
        super().keyPressEvent(event)
    
    def set_editable(self, editable: bool) -> None:
        """Set whether the table is editable.
        
        Args:
            editable: If True, the table is editable; otherwise, it's read-only.
        """
        if editable:
            self.setEditTriggers(
                QAbstractItemView.DoubleClicked | 
                QAbstractItemView.EditKeyPressed |
                QAbstractItemView.SelectedClicked
            )
        else:
            self.setEditTriggers(QAbstractItemView.NoEditTriggers)