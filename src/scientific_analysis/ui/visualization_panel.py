"""可视化面板

提供用于创建和管理可视化图表的用户界面组件。
"""

from typing import Optional, List, Dict, Any, Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton,
    QLabel, QFormLayout, QScrollArea, QFrame, QSplitter,
    QTabWidget, QToolBar, QSizePolicy, QSpacerItem, QGroupBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from ..visualization import (
    BaseChart, ChartType, LineChart, BarChart, ScatterChart,
    HistogramChart, PieChart, BoxPlot, HeatmapChart, ChartExporter
)
from ..models.dataset import Dataset
from ..data.manager import DataManager


class MatplotlibCanvas(FigureCanvas):
    """Matplotlib画布组件"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """初始化Matplotlib画布
        
        Args:
            parent: 父组件
            width: 宽度（英寸）
            height: 高度（英寸）
            dpi: 分辨率
        """
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        
        # 设置画布属性
        FigureCanvas.setSizePolicy(
            self, QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        FigureCanvas.updateGeometry(self)
        
    def clear(self):
        """清除画布"""
        self.axes.clear()
        self.draw()


class ChartPanel(QWidget):
    """图表面板组件"""
    
    chart_closed = Signal(str)  # 图表关闭信号
    
    def __init__(self, chart: BaseChart, parent=None):
        """初始化图表面板
        
        Args:
            chart: 图表对象
            parent: 父组件
        """
        super().__init__(parent)
        self.chart = chart
        self.chart_id = id(chart)  # 使用对象ID作为唯一标识符
        self.exporter = ChartExporter(chart)
        
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建工具栏
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加标题标签
        title_label = QLabel(self.chart.title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        toolbar_layout.addWidget(title_label)
        
        # 添加弹性空间
        toolbar_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # 添加导出按钮
        self.export_button = QPushButton("导出")
        self.export_button.clicked.connect(self._export_chart)
        toolbar_layout.addWidget(self.export_button)
        
        # 添加关闭按钮
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self._close_chart)
        toolbar_layout.addWidget(self.close_button)
        
        main_layout.addLayout(toolbar_layout)
        
        # 创建Matplotlib画布
        self.canvas = MatplotlibCanvas(self, width=5, height=4, dpi=100)
        main_layout.addWidget(self.canvas)
        
        # 创建Matplotlib工具栏
        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        main_layout.addWidget(self.mpl_toolbar)
        
        # 绘制图表
        self._plot_chart()
        
    def _plot_chart(self):
        """绘制图表"""
        # 清除画布
        self.canvas.clear()
        
        # 调用图表的plot方法
        self.chart.plot(self.canvas.axes)
        
        # 更新画布
        self.canvas.draw()
        
    def _export_chart(self):
        """导出图表"""
        # 创建导出菜单
        from PySide6.QtWidgets import QMenu, QFileDialog
        
        menu = QMenu(self)
        
        # 添加导出选项
        png_action = menu.addAction("导出为PNG")
        jpg_action = menu.addAction("导出为JPG")
        svg_action = menu.addAction("导出为SVG")
        pdf_action = menu.addAction("导出为PDF")
        menu.addSeparator()
        csv_action = menu.addAction("导出数据为CSV")
        
        # 显示菜单
        action = menu.exec_(self.export_button.mapToGlobal(self.export_button.rect().bottomLeft()))
        
        if action == png_action:
            file_path, _ = QFileDialog.getSaveFileName(self, "导出为PNG", "", "PNG文件 (*.png)")
            if file_path:
                self.exporter.export(file_path, 'png')
        elif action == jpg_action:
            file_path, _ = QFileDialog.getSaveFileName(self, "导出为JPG", "", "JPG文件 (*.jpg)")
            if file_path:
                self.exporter.export(file_path, 'jpg')
        elif action == svg_action:
            file_path, _ = QFileDialog.getSaveFileName(self, "导出为SVG", "", "SVG文件 (*.svg)")
            if file_path:
                self.exporter.export(file_path, 'svg')
        elif action == pdf_action:
            file_path, _ = QFileDialog.getSaveFileName(self, "导出为PDF", "", "PDF文件 (*.pdf)")
            if file_path:
                self.exporter.export(file_path, 'pdf')
        elif action == csv_action:
            file_path, _ = QFileDialog.getSaveFileName(self, "导出数据为CSV", "", "CSV文件 (*.csv)")
            if file_path:
                self.exporter.export_data(file_path, 'csv')
                
    def _close_chart(self):
        """关闭图表"""
        # 发送图表关闭信号
        self.chart_closed.emit(str(self.chart_id))
        
    def get_chart_id(self) -> str:
        """获取图表ID
        
        Returns:
            str: 图表ID
        """
        return str(self.chart_id)
        

class VisualizationPanel(QWidget):
    """可视化面板
    
    用于创建和管理可视化图表的面板。
    """
    
    def __init__(self, data_manager: DataManager, parent=None):
        """初始化可视化面板
        
        Args:
            data_manager: 数据管理器
            parent: 父组件
        """
        super().__init__(parent)
        self.data_manager = data_manager
        self.charts = {}  # 存储图表ID和面板的映射
        
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
        
        # 添加图表类型选择下拉框
        self.chart_type_combo = QComboBox()
        for chart_type in ChartType:
            self.chart_type_combo.addItem(chart_type.name)
        control_layout.addRow("图表类型:", self.chart_type_combo)
        
        # 添加X轴变量选择下拉框
        self.x_var_combo = QComboBox()
        control_layout.addRow("X轴变量:", self.x_var_combo)
        
        # 添加Y轴变量选择下拉框
        self.y_var_combo = QComboBox()
        control_layout.addRow("Y轴变量:", self.y_var_combo)
        
        # 添加创建图表按钮
        self.create_chart_button = QPushButton("创建图表")
        self.create_chart_button.clicked.connect(self._create_chart)
        control_layout.addRow("", self.create_chart_button)
        
        main_layout.addWidget(control_panel)
        
        # 创建分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)
        
        # 创建图表容器
        self.charts_container = QTabWidget()
        self.charts_container.setTabsClosable(True)
        self.charts_container.tabCloseRequested.connect(self._close_chart_tab)
        main_layout.addWidget(self.charts_container)
        
        # 连接信号
        self.dataset_combo.currentIndexChanged.connect(self._update_variable_combos)
        
        # 初始化变量下拉框
        self._update_variable_combos()
        
    def _update_dataset_combo(self):
        """更新数据集下拉框"""
        self.dataset_combo.clear()
        
        # 添加数据集
        for dataset_id, dataset in self.data_manager.datasets.items():
            self.dataset_combo.addItem(dataset.name, dataset_id)
            
    def _update_variable_combos(self, index=0):
        """更新变量下拉框
        
        Args:
            index: 当前选中的数据集索引
        """
        self.x_var_combo.clear()
        self.y_var_combo.clear()
        
        # 获取当前数据集
        if self.dataset_combo.count() == 0:
            return
            
        dataset_id = self.dataset_combo.currentData()
        dataset = self.data_manager.get_dataset(dataset_id)
        
        if dataset is None or not hasattr(dataset.data, 'columns'):
            return
            
        # 添加变量
        for column in dataset.data.columns:
            self.x_var_combo.addItem(column)
            self.y_var_combo.addItem(column)
            
    def _create_chart(self):
        """创建图表"""
        # 获取当前选择
        dataset_id = self.dataset_combo.currentData()
        chart_type_name = self.chart_type_combo.currentText()
        x_var = self.x_var_combo.currentText()
        y_var = self.y_var_combo.currentText()
        
        # 获取数据集
        dataset = self.data_manager.get_dataset(dataset_id)
        if dataset is None:
            return
            
        # 创建图表
        chart = self._create_chart_by_type(chart_type_name, dataset, x_var, y_var)
        if chart is None:
            return
            
        # 创建图表面板
        chart_panel = ChartPanel(chart)
        chart_panel.chart_closed.connect(self._close_chart)
        
        # 添加到图表容器
        chart_id = chart_panel.get_chart_id()
        self.charts[chart_id] = chart_panel
        
        # 添加到标签页
        tab_title = f"{chart_type_name}: {x_var} vs {y_var}"
        self.charts_container.addTab(chart_panel, tab_title)
        
        # 选中新创建的标签页
        self.charts_container.setCurrentWidget(chart_panel)
        
    def _create_chart_by_type(self, chart_type_name: str, dataset: Dataset, 
                             x_var: str, y_var: str) -> Optional[BaseChart]:
        """根据类型创建图表
        
        Args:
            chart_type_name: 图表类型名称
            dataset: 数据集
            x_var: X轴变量
            y_var: Y轴变量
            
        Returns:
            Optional[BaseChart]: 创建的图表对象
        """
        # 获取数据
        data = dataset.data
        
        # 检查变量是否存在
        if x_var not in data.columns or y_var not in data.columns:
            return None
            
        # 根据图表类型创建图表
        chart_title = f"{dataset.name}: {y_var} vs {x_var}"
        
        if chart_type_name == ChartType.LINE.name:
            chart = LineChart(title=chart_title)
            chart.set_data(data[x_var].values, data[y_var].values)
            chart.set_labels(x_label=x_var, y_label=y_var)
            return chart
            
        elif chart_type_name == ChartType.BAR.name:
            chart = BarChart(title=chart_title)
            chart.set_data(data[x_var].values, data[y_var].values)
            chart.set_labels(x_label=x_var, y_label=y_var)
            return chart
            
        elif chart_type_name == ChartType.SCATTER.name:
            chart = ScatterChart(title=chart_title)
            chart.set_data(data[x_var].values, data[y_var].values)
            chart.set_labels(x_label=x_var, y_label=y_var)
            return chart
            
        elif chart_type_name == ChartType.HISTOGRAM.name:
            chart = HistogramChart(title=f"{dataset.name}: {x_var} 直方图")
            chart.set_data(data[x_var].values)
            chart.set_labels(x_label=x_var, y_label="频率")
            return chart
            
        elif chart_type_name == ChartType.PIE.name:
            # 对于饼图，我们需要分类数据
            if data[x_var].dtype.name in ['object', 'category']:
                # 如果X是分类变量，计算每个类别的Y值总和
                values = data.groupby(x_var)[y_var].sum().values
                labels = data.groupby(x_var)[y_var].sum().index.tolist()
            else:
                # 否则，计算X的分布
                values = data[x_var].value_counts().values
                labels = data[x_var].value_counts().index.tolist()
                
            chart = PieChart(title=f"{dataset.name}: {x_var} 饼图")
            chart.set_data(values, labels)
            return chart
            
        elif chart_type_name == ChartType.BOX.name:
            chart = BoxPlot(title=f"{dataset.name}: {y_var} 箱线图")
            chart.set_data(data[y_var].values)
            chart.set_labels(x_label="", y_label=y_var)
            return chart
            
        elif chart_type_name == ChartType.HEATMAP.name:
            # 对于热图，我们需要计算相关矩阵
            # 选择所有数值列
            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
            if len(numeric_cols) < 2:
                return None
                
            corr_matrix = data[numeric_cols].corr()
            
            chart = HeatmapChart(title=f"{dataset.name}: 相关性热图")
            chart.set_data(corr_matrix)
            return chart
            
        return None
        
    def _close_chart(self, chart_id: str):
        """关闭图表
        
        Args:
            chart_id: 图表ID
        """
        # 查找图表面板
        if chart_id not in self.charts:
            return
            
        chart_panel = self.charts[chart_id]
        
        # 查找标签页索引
        index = self.charts_container.indexOf(chart_panel)
        if index != -1:
            self.charts_container.removeTab(index)
            
        # 移除图表
        del self.charts[chart_id]
        
    def _close_chart_tab(self, index: int):
        """关闭图表标签页
        
        Args:
            index: 标签页索引
        """
        # 获取标签页组件
        widget = self.charts_container.widget(index)
        
        # 查找图表ID
        chart_id = None
        for cid, panel in self.charts.items():
            if panel == widget:
                chart_id = cid
                break
                
        if chart_id is not None:
            # 移除标签页
            self.charts_container.removeTab(index)
            
            # 移除图表
            del self.charts[chart_id]
            
    def refresh(self):
        """刷新面板"""
        # 更新数据集下拉框
        self._update_dataset_combo()
        
        # 更新变量下拉框
        self._update_variable_combos()