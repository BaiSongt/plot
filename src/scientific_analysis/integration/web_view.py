#!/usr/bin/env python3
"""
Web视图组件
在桌面应用中嵌入Web界面
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtCore import QUrl, Signal, QTimer
from PySide6.QtGui import QIcon
import requests
import time

class WebView(QWidget):
    """Web视图组件"""
    
    # 信号
    page_loaded = Signal(str)  # 页面加载完成
    connection_changed = Signal(bool)  # 连接状态改变
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.web_url = "http://localhost:5173"
        self.backend_url = "http://localhost:8000"
        self.is_connected = False
        
        self.setup_ui()
        self.setup_web_engine()
        self.setup_connection_monitor()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        # URL输入框
        self.url_input = QLineEdit()
        self.url_input.setText(self.web_url)
        self.url_input.returnPressed.connect(self.load_url)
        
        # 按钮
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.refresh)
        
        self.home_btn = QPushButton("主页")
        self.home_btn.clicked.connect(self.go_home)
        
        self.back_btn = QPushButton("后退")
        self.back_btn.clicked.connect(self.go_back)
        
        self.forward_btn = QPushButton("前进")
        self.forward_btn.clicked.connect(self.go_forward)
        
        # 连接状态指示器
        self.status_label = QLabel("连接状态: 检查中...")
        
        # 添加到工具栏
        toolbar.addWidget(QLabel("地址:"))
        toolbar.addWidget(self.url_input)
        toolbar.addWidget(self.refresh_btn)
        toolbar.addWidget(self.home_btn)
        toolbar.addWidget(self.back_btn)
        toolbar.addWidget(self.forward_btn)
        toolbar.addWidget(self.status_label)
        
        layout.addLayout(toolbar)
        
        # Web引擎视图
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        # 连接信号
        self.web_view.loadFinished.connect(self.on_load_finished)
        self.web_view.urlChanged.connect(self.on_url_changed)
    
    def setup_web_engine(self):
        """设置Web引擎"""
        settings = self.web_view.settings()
        
        # 启用开发者工具
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        
        # 加载初始页面
        self.load_url()
    
    def setup_connection_monitor(self):
        """设置连接监控"""
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self.check_connection)
        self.connection_timer.start(5000)  # 每5秒检查一次
        
        # 立即检查一次
        self.check_connection()
    
    def check_connection(self):
        """检查服务连接状态"""
        try:
            # 检查前端服务
            frontend_response = requests.get(self.web_url, timeout=2)
            frontend_ok = frontend_response.status_code == 200
            
            # 检查后端服务
            backend_response = requests.get(f"{self.backend_url}/health", timeout=2)
            backend_ok = backend_response.status_code == 200
            
            if frontend_ok and backend_ok:
                status = "✅ 前端和后端服务正常"
                self.is_connected = True
            elif frontend_ok:
                status = "⚠️ 前端正常，后端离线"
                self.is_connected = False
            elif backend_ok:
                status = "⚠️ 后端正常，前端离线"
                self.is_connected = False
            else:
                status = "❌ 前端和后端服务离线"
                self.is_connected = False
                
        except Exception:
            status = "❌ 服务连接失败"
            self.is_connected = False
        
        self.status_label.setText(f"连接状态: {status}")
        self.connection_changed.emit(self.is_connected)
    
    def load_url(self):
        """加载URL"""
        url = self.url_input.text()
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        self.web_view.setUrl(QUrl(url))
    
    def refresh(self):
        """刷新页面"""
        self.web_view.reload()
    
    def go_home(self):
        """回到主页"""
        self.url_input.setText(self.web_url)
        self.load_url()
    
    def go_back(self):
        """后退"""
        if self.web_view.history().canGoBack():
            self.web_view.back()
    
    def go_forward(self):
        """前进"""
        if self.web_view.history().canGoForward():
            self.web_view.forward()
    
    def on_load_finished(self, success: bool):
        """页面加载完成"""
        if success:
            current_url = self.web_view.url().toString()
            self.page_loaded.emit(current_url)
            
            # 注入JavaScript代码，实现桌面应用与Web页面的通信
            js_code = """
            // 添加桌面应用通信接口
            window.desktopApp = {
                // 发送数据到桌面应用
                sendToDesktop: function(data) {
                    console.log('发送数据到桌面应用:', data);
                    // 这里可以通过Qt的JavaScript桥接实现通信
                },
                
                // 接收来自桌面应用的数据
                receiveFromDesktop: function(data) {
                    console.log('接收来自桌面应用的数据:', data);
                    // 触发自定义事件
                    window.dispatchEvent(new CustomEvent('desktopData', {detail: data}));
                }
            };
            
            // 通知桌面应用页面已加载
            console.log('Web页面已在桌面应用中加载');
            """
            
            self.web_view.page().runJavaScript(js_code)
    
    def on_url_changed(self, url: QUrl):
        """URL改变"""
        self.url_input.setText(url.toString())
    
    def send_data_to_web(self, data: dict):
        """发送数据到Web页面"""
        js_code = f"""
        if (window.desktopApp) {{
            window.desktopApp.receiveFromDesktop({data});
        }}
        """
        self.web_view.page().runJavaScript(js_code)
    
    def set_web_url(self, url: str):
        """设置Web URL"""
        self.web_url = url
        self.url_input.setText(url)
    
    def set_backend_url(self, url: str):
        """设置后端URL"""
        self.backend_url = url
    
    def is_service_connected(self) -> bool:
        """获取服务连接状态"""
        return self.is_connected
    
    def get_current_url(self) -> str:
        """获取当前URL"""
        return self.web_view.url().toString()
    
    def closeEvent(self, event):
        """关闭事件"""
        if hasattr(self, 'connection_timer'):
            self.connection_timer.stop()
        super().closeEvent(event)

class EmbeddedWebWidget(QWidget):
    """嵌入式Web组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建Web视图
        self.web_view = WebView()
        layout.addWidget(self.web_view)
        
        # 连接信号
        self.web_view.connection_changed.connect(self.on_connection_changed)
        self.web_view.page_loaded.connect(self.on_page_loaded)
    
    def on_connection_changed(self, connected: bool):
        """连接状态改变"""
        if connected:
            print("Web服务连接成功")
        else:
            print("Web服务连接失败")
    
    def on_page_loaded(self, url: str):
        """页面加载完成"""
        print(f"页面加载完成: {url}")
    
    def get_web_view(self) -> WebView:
        """获取Web视图"""
        return self.web_view