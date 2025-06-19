#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试数据管理器模块。
"""

import unittest
import os
import tempfile
import pandas as pd
import numpy as np
from scientific_analysis.models.dataset import Dataset
from scientific_analysis.data.manager import DataManager


class TestDataManager(unittest.TestCase):
    """数据管理器的测试用例。"""
    
    def setUp(self):
        """设置测试环境。"""
        # 创建数据管理器
        self.manager = DataManager()
        
        # 创建测试数据集
        data1 = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50],
            'C': ['a', 'b', 'c', 'd', 'e']
        })
        self.dataset1 = Dataset(data=data1, name="测试数据集1")
        
        data2 = pd.DataFrame({
            'X': [1.1, 2.2, 3.3, 4.4, 5.5],
            'Y': [10.1, 20.2, 30.3, 40.4, 50.5],
            'Z': [True, False, True, False, True]
        })
        self.dataset2 = Dataset(data=data2, name="测试数据集2")
        
        # 创建临时目录用于保存文件
        self.temp_dir = tempfile.TemporaryDirectory()
    
    def tearDown(self):
        """清理测试资源。"""
        # 清除临时目录
        self.temp_dir.cleanup()
    
    def test_add_dataset(self):
        """测试添加数据集。"""
        # 添加数据集
        self.manager.add_dataset(self.dataset1)
        
        # 验证数据集是否已添加
        self.assertIn(self.dataset1.name, self.manager.get_dataset_names())
        
        # 验证数据集内容是否正确
        retrieved_dataset = self.manager.get_dataset(self.dataset1.name)
        pd.testing.assert_frame_equal(retrieved_dataset.data, self.dataset1.data)
    
    def test_remove_dataset(self):
        """测试移除数据集。"""
        # 添加数据集
        self.manager.add_dataset(self.dataset1)
        self.manager.add_dataset(self.dataset2)
        
        # 验证数据集是否已添加
        self.assertEqual(len(self.manager.get_dataset_names()), 2)
        
        # 移除数据集
        self.manager.remove_dataset(self.dataset1.name)
        
        # 验证数据集是否已移除
        self.assertEqual(len(self.manager.get_dataset_names()), 1)
        self.assertNotIn(self.dataset1.name, self.manager.get_dataset_names())
        self.assertIn(self.dataset2.name, self.manager.get_dataset_names())
    
    def test_set_current_dataset(self):
        """测试设置当前数据集。"""
        # 添加数据集
        self.manager.add_dataset(self.dataset1)
        self.manager.add_dataset(self.dataset2)
        
        # 设置当前数据集
        self.manager.set_current_dataset(self.dataset2.name)
        
        # 验证当前数据集是否正确
        current_dataset = self.manager.get_current_dataset()
        self.assertEqual(current_dataset.name, self.dataset2.name)
        pd.testing.assert_frame_equal(current_dataset.data, self.dataset2.data)
    
    def test_save_and_load_dataset(self):
        """测试保存和加载数据集。"""
        # 添加数据集
        self.manager.add_dataset(self.dataset1)
        
        # 保存数据集到CSV文件
        file_path = os.path.join(self.temp_dir.name, "test_dataset.csv")
        self.manager.save_dataset(self.dataset1.name, file_path)
        
        # 验证文件是否已创建
        self.assertTrue(os.path.exists(file_path))
        
        # 移除数据集
        self.manager.remove_dataset(self.dataset1.name)
        self.assertEqual(len(self.manager.get_dataset_names()), 0)
        
        # 加载数据集
        self.manager.load_dataset(file_path, "加载的数据集")
        
        # 验证数据集是否已加载
        self.assertIn("加载的数据集", self.manager.get_dataset_names())
        
        # 验证加载的数据集内容是否正确
        loaded_dataset = self.manager.get_dataset("加载的数据集")
        # CSV加载可能会改变数据类型，所以只比较值
        pd.testing.assert_frame_equal(
            loaded_dataset.data, 
            self.dataset1.data,
            check_dtype=False
        )
    
    def test_save_and_load_excel(self):
        """测试保存和加载Excel格式数据集。"""
        # 添加数据集
        self.manager.add_dataset(self.dataset1)
        
        # 保存数据集到Excel文件
        file_path = os.path.join(self.temp_dir.name, "test_dataset.xlsx")
        self.manager.save_dataset(self.dataset1.name, file_path)
        
        # 验证文件是否已创建
        self.assertTrue(os.path.exists(file_path))
        
        # 移除数据集
        self.manager.remove_dataset(self.dataset1.name)
        
        # 加载数据集
        self.manager.load_dataset(file_path, "Excel数据集")
        
        # 验证数据集是否已加载
        self.assertIn("Excel数据集", self.manager.get_dataset_names())
        
        # 验证加载的数据集内容是否正确
        loaded_dataset = self.manager.get_dataset("Excel数据集")
        pd.testing.assert_frame_equal(
            loaded_dataset.data, 
            self.dataset1.data,
            check_dtype=False
        )
    
    def test_clipboard_operations(self):
        """测试剪贴板导入导出操作。"""
        # 这个测试可能在自动化测试环境中不可靠，因为剪贴板访问可能受限
        # 所以我们只测试方法是否存在，不测试实际功能
        self.assertTrue(hasattr(self.manager, 'import_from_clipboard'))
        self.assertTrue(hasattr(self.manager, 'export_to_clipboard'))
    
    def test_dataset_metadata(self):
        """测试数据集元数据。"""
        # 添加带有元数据的数据集
        metadata = {
            'source': '测试来源',
            'description': '这是一个测试数据集',
            'created_at': '2023-01-01'
        }
        self.dataset1.metadata = metadata
        self.manager.add_dataset(self.dataset1)
        
        # 获取数据集并验证元数据
        retrieved_dataset = self.manager.get_dataset(self.dataset1.name)
        self.assertEqual(retrieved_dataset.metadata, metadata)
    
    def test_multiple_datasets(self):
        """测试管理多个数据集。"""
        # 添加多个数据集
        for i in range(5):
            data = pd.DataFrame({
                f'col_{i}_1': np.random.rand(10),
                f'col_{i}_2': np.random.rand(10)
            })
            dataset = Dataset(data=data, name=f"数据集{i}")
            self.manager.add_dataset(dataset)
        
        # 验证所有数据集是否已添加
        dataset_names = self.manager.get_dataset_names()
        self.assertEqual(len(dataset_names), 5)
        
        # 验证数据集名称是否正确
        for i in range(5):
            self.assertIn(f"数据集{i}", dataset_names)
    
    def test_dataset_renaming(self):
        """测试数据集重命名。"""
        # 添加数据集
        self.manager.add_dataset(self.dataset1)
        
        # 重命名数据集
        old_name = self.dataset1.name
        new_name = "重命名后的数据集"
        self.manager.rename_dataset(old_name, new_name)
        
        # 验证数据集是否已重命名
        self.assertNotIn(old_name, self.manager.get_dataset_names())
        self.assertIn(new_name, self.manager.get_dataset_names())
        
        # 验证数据集内容是否保持不变
        renamed_dataset = self.manager.get_dataset(new_name)
        pd.testing.assert_frame_equal(renamed_dataset.data, self.dataset1.data)


if __name__ == '__main__':
    unittest.main()