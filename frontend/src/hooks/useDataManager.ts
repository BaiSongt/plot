import { useState, useEffect } from 'react';
import { message } from 'antd';

export interface DatasetInfo {
  id: string;
  filename: string;
  size: string;
  uploadTime: string;
  status: string;
  columns?: string[];
  rowCount?: number;
  preview?: any[];
  data?: Record<string, any>[];
}

export interface ChartDataPoint {
  name: string;
  value: number;
  [key: string]: any;
}

/**
 * 数据管理Hook
 * 负责处理数据上传、获取、分析等功能
 */
export const useDataManager = () => {
  const [dataList, setDataList] = useState<DatasetInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedDataset, setSelectedDataset] = useState<DatasetInfo | null>(null);
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);

  // 获取数据集列表
  const fetchDataList = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/datasets/');
      if (response.ok) {
        const data = await response.json();
        setDataList(data);
      } else {
        // 如果API不可用，使用模拟数据
        const mockData: DatasetInfo[] = [
          {
            id: '1',
            filename: 'sample_data.csv',
            size: '2.5 MB',
            uploadTime: '2024-01-15 10:30:00',
            status: '已处理',
            columns: ['name', 'value', 'category'],
            rowCount: 100
          }
        ];
        setDataList(mockData);
      }
    } catch (error) {
      console.error('获取数据列表失败:', error);
      // 使用模拟数据作为后备
      const mockData: DatasetInfo[] = [
        {
          id: '1',
          filename: 'sample_data.csv',
          size: '2.5 MB',
          uploadTime: '2024-01-15 10:30:00',
          status: '已处理',
          columns: ['name', 'value', 'category'],
          rowCount: 100
        }
      ];
      setDataList(mockData);
    } finally {
      setLoading(false);
    }
  };

  // 获取数据集详情
  const fetchDatasetDetail = async (datasetId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/datasets/${datasetId}`);
      if (response.ok) {
        const data = await response.json();
        setSelectedDataset(data);
        return data;
      } else {
        throw new Error('获取数据集详情失败');
      }
    } catch (error) {
      console.error('获取数据集详情失败:', error);
      message.error('获取数据集详情失败');
      return null;
    } finally {
      setLoading(false);
    }
  };

  // 获取图表数据
  const fetchChartData = async (datasetId: string, chartType: string) => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/datasets/${datasetId}/chart-data?type=${chartType}`);
      if (response.ok) {
        const data = await response.json();
        setChartData(data);
        return data;
      } else {
        // 使用模拟数据
        const mockChartData = generateMockChartData(chartType);
        setChartData(mockChartData);
        return mockChartData;
      }
    } catch (error) {
      console.error('获取图表数据失败:', error);
      // 使用模拟数据作为后备
      const mockChartData = generateMockChartData(chartType);
      setChartData(mockChartData);
      return mockChartData;
    } finally {
      setLoading(false);
    }
  };

  // 生成模拟图表数据
  const generateMockChartData = (chartType: string): ChartDataPoint[] => {
    switch (chartType) {
      case 'bar':
        return [
          { name: '产品A', value: 120 },
          { name: '产品B', value: 200 },
          { name: '产品C', value: 150 },
          { name: '产品D', value: 80 },
          { name: '产品E', value: 70 }
        ];
      case 'line':
        return [
          { name: '1月', value: 820 },
          { name: '2月', value: 932 },
          { name: '3月', value: 901 },
          { name: '4月', value: 934 },
          { name: '5月', value: 1290 },
          { name: '6月', value: 1330 }
        ];
      case 'pie':
        return [
          { name: '直接访问', value: 335 },
          { name: '邮件营销', value: 310 },
          { name: '联盟广告', value: 234 },
          { name: '视频广告', value: 135 },
          { name: '搜索引擎', value: 1548 }
        ];
      case 'scatter':
        return Array.from({ length: 50 }, (_, i) => ({
          name: `点${i + 1}`,
          value: Math.random() * 100,
          x: Math.random() * 100,
          y: Math.random() * 100
        }));
      default:
        return [];
    }
  };

  // 删除数据集
  const deleteDataset = async (datasetId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/datasets/${datasetId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        message.success('数据集删除成功');
        fetchDataList(); // 刷新列表
      } else {
        throw new Error('删除失败');
      }
    } catch (error) {
      console.error('删除数据集失败:', error);
      message.error('删除数据集失败');
    }
  };

  // 初始化时获取数据列表
  useEffect(() => {
    fetchDataList();
  }, []);

  return {
    dataList,
    loading,
    selectedDataset,
    chartData,
    fetchDataList,
    fetchDatasetDetail,
    fetchChartData,
    deleteDataset,
    setSelectedDataset
  };
};