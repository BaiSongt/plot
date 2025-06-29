from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QCheckBox,
    QMessageBox, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap, QIcon
import requests
import json


class LoginWorker(QThread):
    """登录工作线程"""
    login_success = Signal(dict)  # 登录成功信号，传递用户信息
    login_failed = Signal(str)    # 登录失败信号，传递错误信息
    
    def __init__(self, base_url: str, username: str, password: str):
        super().__init__()
        self.base_url = base_url
        self.username = username
        self.password = password
    
    def run(self):
        try:
            # 构建登录请求
            login_url = f"{self.base_url}/api/v1/auth/login"
            data = {
                "username": self.username,
                "password": self.password
            }
            
            # 发送登录请求
            response = requests.post(
                login_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.login_success.emit(result)
            else:
                error_msg = "登录失败"
                try:
                    error_detail = response.json().get("detail", "未知错误")
                    error_msg = f"登录失败: {error_detail}"
                except:
                    error_msg = f"登录失败: HTTP {response.status_code}"
                self.login_failed.emit(error_msg)
                
        except requests.exceptions.ConnectionError:
            self.login_failed.emit("无法连接到服务器，请检查网络连接")
        except requests.exceptions.Timeout:
            self.login_failed.emit("连接超时，请稍后重试")
        except Exception as e:
            self.login_failed.emit(f"登录过程中发生错误: {str(e)}")


class LoginDialog(QDialog):
    """登录对话框"""
    
    def __init__(self, parent=None, base_url: str = "http://localhost:8000"):
        super().__init__(parent)
        self.base_url = base_url
        self.user_info = None
        self.login_worker = None
        
        self.setWindowTitle("登录到后端服务")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        self.setup_ui()
        self.load_saved_credentials()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("科学数据分析工具")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin: 10px 0;
            }
        """)
        layout.addWidget(title_label)
        
        # 服务器地址
        server_layout = QHBoxLayout()
        server_label = QLabel("服务器:")
        self.server_edit = QLineEdit(self.base_url)
        server_layout.addWidget(server_label)
        server_layout.addWidget(self.server_edit)
        layout.addLayout(server_layout)
        
        # 登录表单
        form_layout = QFormLayout()
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("请输入用户名")
        form_layout.addRow("用户名:", self.username_edit)
        
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("请输入密码")
        self.password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("密码:", self.password_edit)
        
        layout.addLayout(form_layout)
        
        # 记住密码选项
        self.remember_checkbox = QCheckBox("记住登录信息")
        layout.addWidget(self.remember_checkbox)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #e74c3c;")
        layout.addWidget(self.status_label)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.login_button = QPushButton("登录")
        self.login_button.setDefault(True)
        self.login_button.clicked.connect(self.login)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        # 连接回车键
        self.password_edit.returnPressed.connect(self.login)
    
    def load_saved_credentials(self):
        """加载保存的登录信息"""
        try:
            # 这里可以从配置文件或注册表加载保存的登录信息
            # 暂时使用简单的实现
            pass
        except Exception as e:
            print(f"加载登录信息失败: {e}")
    
    def save_credentials(self):
        """保存登录信息"""
        if self.remember_checkbox.isChecked():
            try:
                # 这里可以保存到配置文件或注册表
                # 注意：密码应该加密保存
                pass
            except Exception as e:
                print(f"保存登录信息失败: {e}")
    
    def login(self):
        """执行登录"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        server_url = self.server_edit.text().strip()
        
        if not username:
            self.show_error("请输入用户名")
            self.username_edit.setFocus()
            return
        
        if not password:
            self.show_error("请输入密码")
            self.password_edit.setFocus()
            return
        
        if not server_url:
            self.show_error("请输入服务器地址")
            self.server_edit.setFocus()
            return
        
        # 开始登录
        self.set_login_state(True)
        self.base_url = server_url
        
        # 创建登录工作线程
        self.login_worker = LoginWorker(server_url, username, password)
        self.login_worker.login_success.connect(self.on_login_success)
        self.login_worker.login_failed.connect(self.on_login_failed)
        self.login_worker.start()
    
    def set_login_state(self, logging_in: bool):
        """设置登录状态"""
        self.login_button.setEnabled(not logging_in)
        self.username_edit.setEnabled(not logging_in)
        self.password_edit.setEnabled(not logging_in)
        self.server_edit.setEnabled(not logging_in)
        
        if logging_in:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # 无限进度条
            self.status_label.setText("正在登录...")
            self.status_label.setStyleSheet("color: #3498db;")
        else:
            self.progress_bar.setVisible(False)
            self.status_label.setText("")
    
    def on_login_success(self, user_info: dict):
        """登录成功处理"""
        self.set_login_state(False)
        self.user_info = user_info
        self.save_credentials()
        
        self.status_label.setText("登录成功!")
        self.status_label.setStyleSheet("color: #27ae60;")
        
        # 延迟关闭对话框
        QThread.msleep(500)
        self.accept()
    
    def on_login_failed(self, error_msg: str):
        """登录失败处理"""
        self.set_login_state(False)
        self.show_error(error_msg)
    
    def show_error(self, message: str):
        """显示错误信息"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #e74c3c;")
    
    def get_user_info(self) -> dict:
        """获取用户信息"""
        return self.user_info
    
    def get_base_url(self) -> str:
        """获取服务器地址"""
        return self.base_url