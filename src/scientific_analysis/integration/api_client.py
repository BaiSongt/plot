#!/usr/bin/env python3
"""
后端API客户端
用于桌面应用与后端服务通信
"""

import requests
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

class APIClient:
    """后端API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.token = None
        
    def set_auth_token(self, token: str):
        """设置认证令牌"""
        self.token = token
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })
    
    def is_connected(self) -> bool:
        """检查后端连接状态"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def login(self, username: str, password: str) -> bool:
        """用户登录"""
        try:
            data = {
                "username": username,
                "password": password
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                self.set_auth_token(result.get('access_token'))
                return True
            return False
        except Exception as e:
            print(f"登录失败: {e}")
            return False
    
    def upload_dataset(self, data: pd.DataFrame, name: str, description: str = "") -> Optional[Dict]:
        """上传数据集到后端"""
        try:
            # 将DataFrame转换为JSON格式
            dataset_json = {
                "name": name,
                "description": description,
                "data": data.to_dict('records'),
                "columns": list(data.columns),
                "shape": list(data.shape),
                "dtypes": {col: str(dtype) for col, dtype in data.dtypes.items()},
                "created_at": datetime.now().isoformat()
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/datasets/",
                json=dataset_json
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                print(f"上传失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"上传数据集失败: {e}")
            return None
    
    def get_datasets(self) -> List[Dict]:
        """获取用户的所有数据集"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/datasets/")
            
            if response.status_code == 200:
                return response.json()
            return []
            
        except Exception as e:
            print(f"获取数据集失败: {e}")
            return []
    
    def download_dataset(self, dataset_id: int) -> Optional[pd.DataFrame]:
        """下载数据集"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/datasets/{dataset_id}")
            
            if response.status_code == 200:
                dataset_info = response.json()
                data = pd.DataFrame(dataset_info['data'])
                return data
            return None
            
        except Exception as e:
            print(f"下载数据集失败: {e}")
            return None
    
    def create_visualization(self, viz_data: Dict) -> Optional[Dict]:
        """创建可视化"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/visualizations/",
                json=viz_data
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                print(f"创建可视化失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"创建可视化失败: {e}")
            return None
    
    def get_visualizations(self) -> List[Dict]:
        """获取用户的所有可视化"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/visualizations/")
            
            if response.status_code == 200:
                return response.json()
            return []
            
        except Exception as e:
            print(f"获取可视化失败: {e}")
            return []
    
    def sync_data_to_backend(self, local_data: Dict) -> bool:
        """同步本地数据到后端"""
        try:
            # 同步数据集
            for dataset_name, dataset_df in local_data.get('datasets', {}).items():
                result = self.upload_dataset(
                    data=dataset_df,
                    name=dataset_name,
                    description=f"从桌面应用同步: {dataset_name}"
                )
                if not result:
                    print(f"同步数据集 {dataset_name} 失败")
                    return False
            
            # 同步可视化配置
            for viz_config in local_data.get('visualizations', []):
                result = self.create_visualization(viz_config)
                if not result:
                    print(f"同步可视化配置失败")
                    return False
            
            return True
            
        except Exception as e:
            print(f"数据同步失败: {e}")
            return False
    
    def sync_data_from_backend(self) -> Dict:
        """从后端同步数据到本地"""
        try:
            synced_data = {
                'datasets': {},
                'visualizations': []
            }
            
            # 获取数据集
            datasets = self.get_datasets()
            for dataset_info in datasets:
                dataset_id = dataset_info['id']
                dataset_name = dataset_info['name']
                
                dataset_df = self.download_dataset(dataset_id)
                if dataset_df is not None:
                    synced_data['datasets'][dataset_name] = dataset_df
            
            # 获取可视化配置
            visualizations = self.get_visualizations()
            synced_data['visualizations'] = visualizations
            
            return synced_data
            
        except Exception as e:
            print(f"从后端同步数据失败: {e}")
            return {'datasets': {}, 'visualizations': []}
    
    def get_analysis_results(self, analysis_type: str, params: Dict) -> Optional[Dict]:
        """获取分析结果"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/analysis/{analysis_type}",
                json=params
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            print(f"获取分析结果失败: {e}")
            return None
    
    def close(self):
        """关闭连接"""
        self.session.close()

# 全局API客户端实例
api_client = APIClient()

def get_api_client() -> APIClient:
    """获取API客户端实例"""
    return api_client