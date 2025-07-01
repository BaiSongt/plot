import React, { useState, useEffect } from 'react';
import { Card, Select, Button, Space, Spin, Empty, message } from 'antd';
import { ReloadOutlined, DownloadOutlined } from '@ant-design/icons';
import BarChart from './charts/BarChart';
import LineChart from './charts/LineChart';
import PieChart from './charts/PieChart';
import ScatterChart from './charts/ScatterChart';
import Scatter3D from './charts/Scatter3D';
import { useDataManager } from '../hooks/useDataManager';
import type { ChartDataPoint } from '../hooks/useDataManager';

const { Option } = Select;

interface ChartContainerProps {
  chartType: 'bar' | 'line' | 'pie' | 'scatter' | 'scatter3d';
  title: string;
}

/**
 * 图表容器组件
 * 负责数据获取、图表渲染和交互功能
 */
const ChartContainer: React.FC<ChartContainerProps> = ({ chartType, title }) => {
  const { dataList, loading, fetchChartData } = useDataManager();
  const [selectedDataset, setSelectedDataset] = useState<string>('');
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [chartLoading, setChartLoading] = useState(false);

  // 加载图表数据
  const loadChartData = async () => {
    if (!selectedDataset) {
      message.warning('请先选择数据集');
      return;
    }

    setChartLoading(true);
    try {
      const data = await fetchChartData(selectedDataset, chartType);
      setChartData(data || []);
    } catch (error) {
      console.error('加载图表数据失败:', error);
      message.error('加载图表数据失败');
    } finally {
      setChartLoading(false);
    }
  };

  // 当选择的数据集改变时自动加载数据
  useEffect(() => {
    if (selectedDataset) {
      loadChartData();
    }
  }, [selectedDataset, chartType]);

  // 渲染对应的图表组件
  const renderChart = () => {
    if (chartLoading) {
      return (
        <div style={{ textAlign: 'center', padding: '60px' }}>
          <Spin size="large" />
          <p style={{ marginTop: '16px' }}>正在加载图表数据...</p>
        </div>
      );
    }

    if (!chartData || chartData.length === 0) {
      return (
        <Empty
          description="暂无数据"
          style={{ padding: '60px' }}
        >
          <Button type="primary" onClick={loadChartData}>
            重新加载
          </Button>
        </Empty>
      );
    }

    const commonProps = {
      data: chartData,
      title: title,
      width: '100%',
      height: '400px'
    };

    switch (chartType) {
      case 'bar':
        return (
          <BarChart
            {...commonProps}
            showLabel={true}
            barBorderRadius={4}
          />
        );
      case 'line':
        return (
          <LineChart
            {...commonProps}
            smooth={true}
            areaStyle={true}
          />
        );
      case 'pie':
        return (
          <PieChart
            {...commonProps}
            showLabel={true}
          />
        );
      case 'scatter':
        return (
          <ScatterChart
            {...commonProps}
            data={chartData.map(item => ({
              ...item,
              x: item.x || Math.random() * 100,
              y: item.y || Math.random() * 100
            }))}
          />
        );
      case 'scatter3d':
        return (
          <Scatter3D
            {...commonProps}
            data={chartData.map(item => ({
              ...item,
              x: item.x || Math.random() * 100,
              y: item.y || Math.random() * 100,
              z: item.value || Math.random() * 100
            }))}
          />
        );
      default:
        return <div>不支持的图表类型</div>;
    }
  };

  // 导出图表
  const exportChart = () => {
    message.info('导出功能开发中...');
  };

  return (
    <Card
      title={title}
      style={{ margin: '16px' }}
      extra={
        <Space>
          <Select
            placeholder="选择数据集"
            style={{ width: 200 }}
            value={selectedDataset}
            onChange={setSelectedDataset}
            loading={loading}
          >
            {dataList.map(dataset => (
              <Option key={dataset.id} value={dataset.id}>
                {dataset.filename}
              </Option>
            ))}
          </Select>
          <Button
            icon={<ReloadOutlined />}
            onClick={loadChartData}
            disabled={!selectedDataset}
          >
            刷新
          </Button>
          <Button
            icon={<DownloadOutlined />}
            onClick={exportChart}
            disabled={!chartData || chartData.length === 0}
          >
            导出
          </Button>
        </Space>
      }
    >
      {renderChart()}
    </Card>
  );
};

export default ChartContainer;
