"""分析面板

提供用于执行和展示数据分析的用户界面组件。
"""

from typing import Optional, List, Dict, Any, Callable, Tuple
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton,
    QLabel, QFormLayout, QScrollArea, QFrame, QSplitter,
    QTabWidget, QToolBar, QSizePolicy, QSpacerItem, QGroupBox,
    QListWidget, QListWidgetItem, QTextEdit, QCheckBox, QSpinBox,
    QDoubleSpinBox, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon

import pandas as pd
import numpy as np

from scientific_analysis.analysis import (
    BaseAnalyzer, AnalysisResult, DescriptiveAnalyzer,
    CorrelationAnalyzer, RegressionAnalyzer, RegressionType,
    ClusteringAnalyzer, ClusteringMethod
)
from scientific_analysis.models.dataset import Dataset
from scientific_analysis.data.manager import DataManager
from .visualization_panel import ChartPanel


class AnalysisResultPanel(QWidget):
    """分析结果面板
    
    用于展示分析结果的面板。
    """
    
    def __init__(self, result: AnalysisResult, parent=None):
        """初始化分析结果面板
        
        Args:
            result: 分析结果
            parent: 父组件
        """
        super().__init__(parent)
        self.result = result
        self.chart_panels = {}  # 存储图表ID和面板的映射
        
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建分析类型标签
        analysis_type = self.result.metadata.get('analysis_type', '未知分析')
        type_label = QLabel(f"分析类型: {analysis_type}")
        type_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(type_label)
        
        # 创建标签页组件
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # 添加结果数据标签页
        data_widget = self._create_data_widget()
        tab_widget.addTab(data_widget, "数据")
        
        # 添加元数据标签页
        metadata_widget = self._create_metadata_widget()
        tab_widget.addTab(metadata_widget, "元数据")
        
        # 添加图表标签页
        if self.result.charts:
            charts_widget = self._create_charts_widget()
            tab_widget.addTab(charts_widget, "图表")
            
    def _create_data_widget(self) -> QWidget:
        """创建数据展示组件
        
        Returns:
            QWidget: 数据展示组件
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 创建表格
        table = QTableWidget()
        layout.addWidget(table)
        
        # 填充表格
        data = self.result.data
        if isinstance(data, pd.DataFrame):
            # 设置行数和列数
            table.setRowCount(len(data))
            table.setColumnCount(len(data.columns))
            
            # 设置表头
            table.setHorizontalHeaderLabels(data.columns.tolist())
            table.setVerticalHeaderLabels([str(i) for i in data.index])
            
            # 填充数据
            for i, (_, row) in enumerate(data.iterrows()):
                for j, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    table.setItem(i, j, item)
                    
            # 调整列宽
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        elif isinstance(data, dict):
            # 对于字典数据，创建键值对表格
            table.setRowCount(len(data))
            table.setColumnCount(2)
            
            # 设置表头
            table.setHorizontalHeaderLabels(["键", "值"])
            
            # 填充数据
            for i, (key, value) in enumerate(data.items()):
                key_item = QTableWidgetItem(str(key))
                table.setItem(i, 0, key_item)
                
                # 处理不同类型的值
                if isinstance(value, (dict, list)):
                    value_str = str(value)
                else:
                    value_str = str(value)
                    
                value_item = QTableWidgetItem(value_str)
                table.setItem(i, 1, value_item)
                
            # 调整列宽
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
        return widget
        
    def _create_metadata_widget(self) -> QWidget:
        """创建元数据展示组件
        
        Returns:
            QWidget: 元数据展示组件
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 创建表格
        table = QTableWidget()
        layout.addWidget(table)
        
        # 填充表格
        metadata = self.result.metadata
        if isinstance(metadata, dict):
            # 设置行数和列数
            table.setRowCount(len(metadata))
            table.setColumnCount(2)
            
            # 设置表头
            table.setHorizontalHeaderLabels(["键", "值"])
            
            # 填充数据
            for i, (key, value) in enumerate(metadata.items()):
                key_item = QTableWidgetItem(str(key))
                table.setItem(i, 0, key_item)
                
                # 处理不同类型的值
                if isinstance(value, (dict, list)):
                    value_str = str(value)
                else:
                    value_str = str(value)
                    
                value_item = QTableWidgetItem(value_str)
                table.setItem(i, 1, value_item)
                
            # 调整列宽
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
        return widget
        
    def _create_charts_widget(self) -> QWidget:
        """创建图表展示组件
        
        Returns:
            QWidget: 图表展示组件
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 创建标签页组件
        charts_tab = QTabWidget()
        layout.addWidget(charts_tab)
        
        # 添加图表
        for i, chart in enumerate(self.result.charts):
            # 创建图表面板
            chart_panel = ChartPanel(chart)
            chart_id = chart_panel.get_chart_id()
            self.chart_panels[chart_id] = chart_panel
            
            # 添加到标签页
            charts_tab.addTab(chart_panel, f"图表 {i+1}: {chart.title}")
            
        return widget


class AnalysisConfigDialog(QDialog):
    """分析配置对话框
    
    用于配置分析参数的对话框。
    """
    
    def __init__(self, analysis_type: str, dataset: Dataset, parent=None):
        """初始化分析配置对话框
        
        Args:
            analysis_type: 分析类型
            dataset: 数据集
            parent: 父组件
        """
        super().__init__(parent)
        self.analysis_type = analysis_type
        self.dataset = dataset
        self.config = {}  # 存储配置参数
        
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        # 设置窗口标题
        self.setWindowTitle(f"{self.analysis_type}分析配置")
        self.resize(500, 400)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建表单布局
        form_layout = QFormLayout()
        main_layout.addLayout(form_layout)
        
        # 根据分析类型创建不同的配置表单
        if self.analysis_type == "描述性统计":
            self._create_descriptive_form(form_layout)
        elif self.analysis_type == "相关性分析":
            self._create_correlation_form(form_layout)
        elif self.analysis_type == "回归分析":
            self._create_regression_form(form_layout)
        elif self.analysis_type == "聚类分析":
            self._create_clustering_form(form_layout)
            
        # 创建按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
    def _create_descriptive_form(self, form_layout: QFormLayout):
        """创建描述性统计配置表单
        
        Args:
            form_layout: 表单布局
        """
        # 创建变量选择列表
        self.variables_list = QListWidget()
        self.variables_list.setSelectionMode(QListWidget.MultiSelection)
        
        # 添加数据集的列
        if hasattr(self.dataset.data, 'columns'):
            for column in self.dataset.data.columns:
                item = QListWidgetItem(column)
                self.variables_list.addItem(item)
                
        form_layout.addRow("选择变量:", self.variables_list)
        
        # 添加计算选项
        self.basic_stats_check = QCheckBox("基本统计量")
        self.basic_stats_check.setChecked(True)
        form_layout.addRow("", self.basic_stats_check)
        
        self.distribution_stats_check = QCheckBox("分布统计量")
        self.distribution_stats_check.setChecked(True)
        form_layout.addRow("", self.distribution_stats_check)
        
        self.frequency_table_check = QCheckBox("频率表")
        self.frequency_table_check.setChecked(False)
        form_layout.addRow("", self.frequency_table_check)
        
        self.outliers_check = QCheckBox("异常值检测")
        self.outliers_check.setChecked(True)
        form_layout.addRow("", self.outliers_check)
        
        # 添加图表选项
        self.include_charts_check = QCheckBox("包含图表")
        self.include_charts_check.setChecked(True)
        form_layout.addRow("", self.include_charts_check)
        
    def _create_correlation_form(self, form_layout: QFormLayout):
        """创建相关性分析配置表单
        
        Args:
            form_layout: 表单布局
        """
        # 创建变量选择列表
        self.variables_list = QListWidget()
        self.variables_list.setSelectionMode(QListWidget.MultiSelection)
        
        # 添加数据集的数值列
        if hasattr(self.dataset.data, 'columns'):
            numeric_cols = self.dataset.data.select_dtypes(include=['number']).columns.tolist()
            for column in numeric_cols:
                item = QListWidgetItem(column)
                self.variables_list.addItem(item)
                
        form_layout.addRow("选择变量:", self.variables_list)
        
        # 添加相关系数方法选择
        self.method_combo = QComboBox()
        self.method_combo.addItems(["pearson", "spearman", "kendall"])
        form_layout.addRow("相关系数方法:", self.method_combo)
        
        # 添加显著性水平设置
        self.alpha_spin = QDoubleSpinBox()
        self.alpha_spin.setRange(0.01, 0.1)
        self.alpha_spin.setSingleStep(0.01)
        self.alpha_spin.setValue(0.05)
        form_layout.addRow("显著性水平:", self.alpha_spin)
        
        # 添加图表选项
        self.include_charts_check = QCheckBox("包含图表")
        self.include_charts_check.setChecked(True)
        form_layout.addRow("", self.include_charts_check)
        
    def _create_regression_form(self, form_layout: QFormLayout):
        """创建回归分析配置表单
        
        Args:
            form_layout: 表单布局
        """
        # 添加回归类型选择
        self.regression_type_combo = QComboBox()
        for reg_type in RegressionType:
            self.regression_type_combo.addItem(reg_type.name)
        form_layout.addRow("回归类型:", self.regression_type_combo)
        
        # 添加因变量选择
        self.dependent_var_combo = QComboBox()
        
        # 添加自变量选择列表
        self.independent_vars_list = QListWidget()
        self.independent_vars_list.setSelectionMode(QListWidget.MultiSelection)
        
        # 添加数据集的数值列
        if hasattr(self.dataset.data, 'columns'):
            numeric_cols = self.dataset.data.select_dtypes(include=['number']).columns.tolist()
            for column in numeric_cols:
                self.dependent_var_combo.addItem(column)
                item = QListWidgetItem(column)
                self.independent_vars_list.addItem(item)
                
        form_layout.addRow("因变量:", self.dependent_var_combo)
        form_layout.addRow("自变量:", self.independent_vars_list)
        
        # 添加多项式回归阶数设置
        self.polynomial_degree_spin = QSpinBox()
        self.polynomial_degree_spin.setRange(2, 5)
        self.polynomial_degree_spin.setValue(2)
        form_layout.addRow("多项式阶数:", self.polynomial_degree_spin)
        
        # 添加图表选项
        self.include_charts_check = QCheckBox("包含图表")
        self.include_charts_check.setChecked(True)
        form_layout.addRow("", self.include_charts_check)
        
    def _create_clustering_form(self, form_layout: QFormLayout):
        """创建聚类分析配置表单
        
        Args:
            form_layout: 表单布局
        """
        # 添加聚类方法选择
        self.clustering_method_combo = QComboBox()
        for method in ClusteringMethod:
            self.clustering_method_combo.addItem(method.name)
        form_layout.addRow("聚类方法:", self.clustering_method_combo)
        
        # 添加特征选择列表
        self.features_list = QListWidget()
        self.features_list.setSelectionMode(QListWidget.MultiSelection)
        
        # 添加数据集的数值列
        if hasattr(self.dataset.data, 'columns'):
            numeric_cols = self.dataset.data.select_dtypes(include=['number']).columns.tolist()
            for column in numeric_cols:
                item = QListWidgetItem(column)
                self.features_list.addItem(item)
                
        form_layout.addRow("选择特征:", self.features_list)
        
        # 添加聚类数量设置
        self.n_clusters_spin = QSpinBox()
        self.n_clusters_spin.setRange(2, 10)
        self.n_clusters_spin.setValue(3)
        form_layout.addRow("聚类数量:", self.n_clusters_spin)
        
        # 添加标准化选项
        self.standardize_check = QCheckBox("标准化数据")
        self.standardize_check.setChecked(True)
        form_layout.addRow("", self.standardize_check)
        
        # 添加DBSCAN参数
        self.eps_spin = QDoubleSpinBox()
        self.eps_spin.setRange(0.1, 5.0)
        self.eps_spin.setSingleStep(0.1)
        self.eps_spin.setValue(0.5)
        form_layout.addRow("DBSCAN邻域半径:", self.eps_spin)
        
        self.min_samples_spin = QSpinBox()
        self.min_samples_spin.setRange(2, 20)
        self.min_samples_spin.setValue(5)
        form_layout.addRow("DBSCAN最小样本数:", self.min_samples_spin)
        
        # 添加图表选项
        self.include_charts_check = QCheckBox("包含图表")
        self.include_charts_check.setChecked(True)
        form_layout.addRow("", self.include_charts_check)
        
    def get_config(self) -> Dict[str, Any]:
        """获取配置参数
        
        Returns:
            Dict[str, Any]: 配置参数
        """
        # 根据分析类型获取不同的配置参数
        if self.analysis_type == "描述性统计":
            return self._get_descriptive_config()
        elif self.analysis_type == "相关性分析":
            return self._get_correlation_config()
        elif self.analysis_type == "回归分析":
            return self._get_regression_config()
        elif self.analysis_type == "聚类分析":
            return self._get_clustering_config()
            
        return {}
        
    def _get_descriptive_config(self) -> Dict[str, Any]:
        """获取描述性统计配置参数
        
        Returns:
            Dict[str, Any]: 配置参数
        """
        # 获取选中的变量
        variables = [item.text() for item in self.variables_list.selectedItems()]
        
        # 获取计算选项
        basic_stats = self.basic_stats_check.isChecked()
        distribution_stats = self.distribution_stats_check.isChecked()
        frequency_table = self.frequency_table_check.isChecked()
        outliers = self.outliers_check.isChecked()
        
        # 获取图表选项
        include_charts = self.include_charts_check.isChecked()
        
        return {
            'variables': variables,
            'basic_stats': basic_stats,
            'distribution_stats': distribution_stats,
            'frequency_table': frequency_table,
            'outliers': outliers,
            'include_charts': include_charts
        }
        
    def _get_correlation_config(self) -> Dict[str, Any]:
        """获取相关性分析配置参数
        
        Returns:
            Dict[str, Any]: 配置参数
        """
        # 获取选中的变量
        variables = [item.text() for item in self.variables_list.selectedItems()]
        
        # 获取相关系数方法
        method = self.method_combo.currentText()
        
        # 获取显著性水平
        alpha = self.alpha_spin.value()
        
        # 获取图表选项
        include_charts = self.include_charts_check.isChecked()
        
        return {
            'variables': variables,
            'method': method,
            'alpha': alpha,
            'include_charts': include_charts
        }
        
    def _get_regression_config(self) -> Dict[str, Any]:
        """获取回归分析配置参数
        
        Returns:
            Dict[str, Any]: 配置参数
        """
        # 获取回归类型
        regression_type_name = self.regression_type_combo.currentText()
        regression_type = RegressionType[regression_type_name]
        
        # 获取因变量
        dependent_var = self.dependent_var_combo.currentText()
        
        # 获取自变量
        independent_vars = [item.text() for item in self.independent_vars_list.selectedItems()]
        
        # 获取多项式阶数
        polynomial_degree = self.polynomial_degree_spin.value()
        
        # 获取图表选项
        include_charts = self.include_charts_check.isChecked()
        
        return {
            'regression_type': regression_type,
            'dependent_var': dependent_var,
            'independent_vars': independent_vars,
            'polynomial_degree': polynomial_degree,
            'include_charts': include_charts
        }
        
    def _get_clustering_config(self) -> Dict[str, Any]:
        """获取聚类分析配置参数
        
        Returns:
            Dict[str, Any]: 配置参数
        """
        # 获取聚类方法
        clustering_method_name = self.clustering_method_combo.currentText()
        clustering_method = ClusteringMethod[clustering_method_name]
        
        # 获取特征
        features = [item.text() for item in self.features_list.selectedItems()]
        
        # 获取聚类数量
        n_clusters = self.n_clusters_spin.value()
        
        # 获取标准化选项
        standardize = self.standardize_check.isChecked()
        
        # 获取DBSCAN参数
        eps = self.eps_spin.value()
        min_samples = self.min_samples_spin.value()
        
        # 获取图表选项
        include_charts = self.include_charts_check.isChecked()
        
        return {
            'method': clustering_method,
            'features': features,
            'n_clusters': n_clusters,
            'standardize': standardize,
            'eps': eps,
            'min_samples': min_samples,
            'include_charts': include_charts
        }


class AnalysisPanel(QWidget):
    """分析面板
    
    用于执行和展示数据分析的面板。
    """
    
    def __init__(self, data_manager: DataManager, parent=None):
        """初始化分析面板
        
        Args:
            data_manager: 数据管理器
            parent: 父组件
        """
        super().__init__(parent)
        self.data_manager = data_manager
        self.results = {}  # 存储分析结果ID和面板的映射
        
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建控制面板
        control_panel = QWidget()
        control_layout = QFormLayout(control_panel)
        
        # 添加数据集选择下拉框
        self.dataset_combo = QComboBox()
        self._update_dataset_combo()
        control_layout.addRow("数据集:", self.dataset_combo)
        
        # 添加分析类型选择下拉框
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems(["描述性统计", "相关性分析", "回归分析", "聚类分析"])
        control_layout.addRow("分析类型:", self.analysis_type_combo)
        
        # 添加执行分析按钮
        self.run_analysis_button = QPushButton("执行分析")
        self.run_analysis_button.clicked.connect(self._run_analysis)
        control_layout.addRow("", self.run_analysis_button)
        
        main_layout.addWidget(control_panel)
        
        # 创建分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)
        
        # 创建结果容器
        self.results_container = QTabWidget()
        self.results_container.setTabsClosable(True)
        self.results_container.tabCloseRequested.connect(self._close_result_tab)
        main_layout.addWidget(self.results_container)
        
    def _update_dataset_combo(self):
        """更新数据集下拉框"""
        self.dataset_combo.clear()
        
        # 添加数据集
        for dataset_id, dataset in self.data_manager.datasets.items():
            self.dataset_combo.addItem(dataset.name, dataset_id)
            
    def _run_analysis(self):
        """执行分析"""
        # 获取当前选择
        dataset_id = self.dataset_combo.currentData()
        analysis_type = self.analysis_type_combo.currentText()
        
        # 获取数据集
        dataset = self.data_manager.get_dataset(dataset_id)
        if dataset is None:
            QMessageBox.warning(self, "错误", "未选择有效的数据集")
            return
            
        # 显示配置对话框
        config_dialog = AnalysisConfigDialog(analysis_type, dataset, self)
        if config_dialog.exec_() != QDialog.Accepted:
            return
            
        # 获取配置参数
        config = config_dialog.get_config()
        
        # 执行分析
        result = self._perform_analysis(analysis_type, dataset, config)
        if result is None:
            QMessageBox.warning(self, "错误", "分析执行失败")
            return
            
        # 创建结果面板
        result_panel = AnalysisResultPanel(result)
        
        # 添加到结果容器
        result_id = id(result)
        self.results[result_id] = result_panel
        
        # 添加到标签页
        tab_title = f"{analysis_type}: {dataset.name}"
        self.results_container.addTab(result_panel, tab_title)
        
        # 选中新创建的标签页
        self.results_container.setCurrentWidget(result_panel)
        
    def _perform_analysis(self, analysis_type: str, dataset: Dataset, 
                         config: Dict[str, Any]) -> Optional[AnalysisResult]:
        """执行分析
        
        Args:
            analysis_type: 分析类型
            dataset: 数据集
            config: 配置参数
            
        Returns:
            Optional[AnalysisResult]: 分析结果
        """
        try:
            if analysis_type == "描述性统计":
                return self._perform_descriptive_analysis(dataset, config)
            elif analysis_type == "相关性分析":
                return self._perform_correlation_analysis(dataset, config)
            elif analysis_type == "回归分析":
                return self._perform_regression_analysis(dataset, config)
            elif analysis_type == "聚类分析":
                return self._perform_clustering_analysis(dataset, config)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"分析执行失败: {str(e)}")
            return None
            
        return None
        
    def _perform_descriptive_analysis(self, dataset: Dataset, 
                                     config: Dict[str, Any]) -> AnalysisResult:
        """执行描述性统计分析
        
        Args:
            dataset: 数据集
            config: 配置参数
            
        Returns:
            AnalysisResult: 分析结果
        """
        # 创建分析器
        analyzer = DescriptiveAnalyzer(dataset)
        
        # 执行分析
        return analyzer.analyze(
            variables=config['variables'],
            basic_stats=config['basic_stats'],
            distribution_stats=config['distribution_stats'],
            frequency_table=config['frequency_table'],
            outliers=config['outliers'],
            include_charts=config['include_charts']
        )
        
    def _perform_correlation_analysis(self, dataset: Dataset, 
                                     config: Dict[str, Any]) -> AnalysisResult:
        """执行相关性分析
        
        Args:
            dataset: 数据集
            config: 配置参数
            
        Returns:
            AnalysisResult: 分析结果
        """
        # 创建分析器
        analyzer = CorrelationAnalyzer(dataset)
        
        # 执行分析
        return analyzer.analyze(
            variables=config['variables'],
            method=config['method'],
            alpha=config['alpha'],
            include_charts=config['include_charts']
        )
        
    def _perform_regression_analysis(self, dataset: Dataset, 
                                    config: Dict[str, Any]) -> AnalysisResult:
        """执行回归分析
        
        Args:
            dataset: 数据集
            config: 配置参数
            
        Returns:
            AnalysisResult: 分析结果
        """
        # 创建分析器
        analyzer = RegressionAnalyzer(dataset)
        
        # 执行分析
        return analyzer.analyze(
            dependent_var=config['dependent_var'],
            independent_vars=config['independent_vars'],
            regression_type=config['regression_type'],
            polynomial_degree=config['polynomial_degree'],
            include_charts=config['include_charts']
        )
        
    def _perform_clustering_analysis(self, dataset: Dataset, 
                                    config: Dict[str, Any]) -> AnalysisResult:
        """执行聚类分析
        
        Args:
            dataset: 数据集
            config: 配置参数
            
        Returns:
            AnalysisResult: 分析结果
        """
        # 创建分析器
        analyzer = ClusteringAnalyzer(dataset)
        
        # 执行分析
        return analyzer.analyze(
            features=config['features'],
            method=config['method'],
            n_clusters=config['n_clusters'],
            standardize=config['standardize'],
            include_charts=config['include_charts'],
            eps=config['eps'],
            min_samples=config['min_samples']
        )
        
    def _close_result_tab(self, index: int):
        """关闭结果标签页
        
        Args:
            index: 标签页索引
        """
        # 获取标签页组件
        widget = self.results_container.widget(index)
        
        # 查找结果ID
        result_id = None
        for rid, panel in self.results.items():
            if panel == widget:
                result_id = rid
                break
                
        if result_id is not None:
            # 移除标签页
            self.results_container.removeTab(index)
            
            # 移除结果
            del self.results[result_id]
            
    def refresh(self):
        """刷新面板"""
        # 更新数据集下拉框
        self._update_dataset_combo()