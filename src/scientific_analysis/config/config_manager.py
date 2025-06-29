import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = None):
        if config_file is None:
            # 默认配置文件路径
            self.config_file = Path(__file__).parent.parent.parent.parent / "config.json"
        else:
            self.config_file = Path(config_file)
        
        self._config = {}
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            else:
                # 如果配置文件不存在，使用默认配置
                self._config = self._get_default_config()
                self.save_config()
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            self._config = self._get_default_config()
        
        return self._config
    
    def save_config(self) -> bool:
        """保存配置文件"""
        try:
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的嵌套键"""
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """设置配置值，支持点号分隔的嵌套键"""
        keys = key.split('.')
        config = self._config
        
        try:
            # 导航到最后一级的父级
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # 设置值
            config[keys[-1]] = value
            return True
        except Exception as e:
            print(f"设置配置值失败: {e}")
            return False
    
    def get_backend_url(self) -> str:
        """获取后端服务器地址"""
        return self.get('backend.url', 'http://localhost:8000')
    
    def set_backend_url(self, url: str) -> bool:
        """设置后端服务器地址"""
        return self.set('backend.url', url)
    
    def get_frontend_url(self) -> str:
        """获取前端服务器地址"""
        return self.get('frontend.url', 'http://localhost:3000')
    
    def set_frontend_url(self, url: str) -> bool:
        """设置前端服务器地址"""
        return self.set('frontend.url', url)
    
    def get_database_url(self) -> str:
        """获取数据库连接地址"""
        return self.get('database.url', 'sqlite:///./scientific_analysis.db')
    
    def get_ui_theme(self) -> str:
        """获取UI主题"""
        return self.get('ui.theme', 'dark')
    
    def set_ui_theme(self, theme: str) -> bool:
        """设置UI主题"""
        return self.set('ui.theme', theme)
    
    def get_language(self) -> str:
        """获取语言设置"""
        return self.get('ui.language', 'zh_CN')
    
    def set_language(self, language: str) -> bool:
        """设置语言"""
        return self.set('ui.language', language)
    
    def is_auto_save_enabled(self) -> bool:
        """是否启用自动保存"""
        return self.get('ui.auto_save', True)
    
    def get_auto_save_interval(self) -> int:
        """获取自动保存间隔（秒）"""
        return self.get('ui.auto_save_interval', 300)
    
    def get_log_level(self) -> str:
        """获取日志级别"""
        return self.get('logging.level', 'INFO')
    
    def get_log_file(self) -> str:
        """获取日志文件路径"""
        return self.get('logging.file', 'logs/app.log')
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "backend": {
                "url": "http://localhost:8000",
                "timeout": 30,
                "retry_attempts": 3
            },
            "frontend": {
                "url": "http://localhost:3000",
                "auto_open": True
            },
            "database": {
                "url": "sqlite:///./scientific_analysis.db"
            },
            "logging": {
                "level": "INFO",
                "file": "logs/app.log",
                "max_size": "10MB",
                "backup_count": 5
            },
            "ui": {
                "theme": "dark",
                "language": "zh_CN",
                "auto_save": True,
                "auto_save_interval": 300
            },
            "data": {
                "default_format": "csv",
                "max_file_size": "100MB",
                "cache_enabled": True,
                "cache_size": "500MB"
            }
        }
    
    def reset_to_default(self) -> bool:
        """重置为默认配置"""
        self._config = self._get_default_config()
        return self.save_config()
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """批量更新配置"""
        try:
            def deep_update(base_dict, update_dict):
                for key, value in update_dict.items():
                    if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                        deep_update(base_dict[key], value)
                    else:
                        base_dict[key] = value
            
            deep_update(self._config, updates)
            return self.save_config()
        except Exception as e:
            print(f"更新配置失败: {e}")
            return False
    
    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._config.copy()


# 全局配置管理器实例
_config_manager = None


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager