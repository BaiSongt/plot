import React, { useState } from 'react';
import {
  Card,
  Button,
  Select,
  Space,
  Radio,
  Checkbox,
  message,
  Row,
  Col,
  Input,
  Form,
  Divider,
} from 'antd';
import {
  DownloadOutlined,
  FileExcelOutlined,
  FilePdfOutlined,
  FileImageOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import { useDataManager } from '../hooks/useDataManager';

const { Option } = Select;
const { TextArea } = Input;

interface ExportOptions {
  format: 'csv' | 'excel' | 'pdf' | 'png' | 'svg' | 'json';
  includeCharts: boolean;
  includeStats: boolean;
  includeRawData: boolean;
  chartTypes: string[];
  customTitle?: string;
  customDescription?: string;
}

/**
 * 数据导出面板组件
 * 提供多种格式的数据和分析结果导出功能
 */
const ExportPanel: React.FC = () => {
  const { dataList } = useDataManager();
  const [selectedDataset, setSelectedDataset] = useState<string>('');
  const [exportOptions, setExportOptions] = useState<ExportOptions>({
    format: 'csv',
    includeCharts: true,
    includeStats: true,
    includeRawData: true,
    chartTypes: ['bar', 'line', 'pie'],
  });
  const [loading, setLoading] = useState(false);

  // 处理导出选项变化
  const handleOptionChange = (key: keyof ExportOptions, value: any) => {
    setExportOptions(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  // 执行导出
  const handleExport = async () => {
    if (!selectedDataset) {
      message.warning('请选择要导出的数据集');
      return;
    }

    setLoading(true);
    try {
      // 构建导出请求
      const exportRequest = {
        datasetId: selectedDataset,
        ...exportOptions,
      };

      // 模拟API调用
      const response = await fetch('/api/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(exportRequest),
      });

      if (!response.ok) {
        throw new Error('导出失败');
      }

      // 获取文件blob
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      
      // 创建下载链接
      const link = document.createElement('a');
      link.href = url;
      
      const dataset = dataList.find(d => d.id === selectedDataset);
      const filename = `${dataset?.filename || 'export'}_${Date.now()}.${exportOptions.format}`;
      link.download = filename;
      
      // 触发下载
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      message.success('导出成功');
    } catch (error) {
      console.warn('API不可用，使用模拟导出:', error);
      
      // 模拟导出功能
      const dataset = dataList.find(d => d.id === selectedDataset);
      const mockData = {
        dataset: dataset?.filename,
        exportTime: new Date().toISOString(),
        format: exportOptions.format,
        options: exportOptions,
        data: 'Mock export data...',
      };
      
      const blob = new Blob([JSON.stringify(mockData, null, 2)], {
        type: 'application/json',
      });
      const url = window.URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `${dataset?.filename || 'export'}_${Date.now()}.json`;
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      message.success('模拟导出完成（实际项目中将调用后端API）');
    } finally {
      setLoading(false);
    }
  };

  // 格式选项
  const formatOptions = [
    { value: 'csv', label: 'CSV文件', icon: <FileTextOutlined /> },
    { value: 'excel', label: 'Excel文件', icon: <FileExcelOutlined /> },
    { value: 'pdf', label: 'PDF报告', icon: <FilePdfOutlined /> },
    { value: 'png', label: 'PNG图片', icon: <FileImageOutlined /> },
    { value: 'svg', label: 'SVG矢量图', icon: <FileImageOutlined /> },
    { value: 'json', label: 'JSON数据', icon: <FileTextOutlined /> },
  ];

  // 图表类型选项
  const chartTypeOptions = [
    { value: 'bar', label: '柱状图' },
    { value: 'line', label: '折线图' },
    { value: 'pie', label: '饼图' },
    { value: 'scatter', label: '散点图' },
    { value: 'heatmap', label: '热力图' },
  ];

  return (
    <Card title="数据导出" style={{ margin: '16px' }}>
      <Form layout="vertical">
        {/* 数据集选择 */}
        <Form.Item label="选择数据集">
          <Select
            placeholder="选择要导出的数据集"
            style={{ width: '100%' }}
            value={selectedDataset}
            onChange={setSelectedDataset}
          >
            {dataList.map(dataset => (
              <Option key={dataset.id} value={dataset.id}>
                {dataset.filename} ({dataset.rows} 行, {dataset.columns?.length || 0} 列)
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Divider />

        {/* 导出格式 */}
        <Form.Item label="导出格式">
          <Radio.Group
            value={exportOptions.format}
            onChange={(e) => handleOptionChange('format', e.target.value)}
          >
            <Row gutter={[16, 16]}>
              {formatOptions.map(option => (
                <Col span={8} key={option.value}>
                  <Radio value={option.value}>
                    <Space>
                      {option.icon}
                      {option.label}
                    </Space>
                  </Radio>
                </Col>
              ))}
            </Row>
          </Radio.Group>
        </Form.Item>

        <Divider />

        {/* 导出内容 */}
        <Form.Item label="导出内容">
          <Space direction="vertical" style={{ width: '100%' }}>
            <Checkbox
              checked={exportOptions.includeRawData}
              onChange={(e) => handleOptionChange('includeRawData', e.target.checked)}
            >
              包含原始数据
            </Checkbox>
            <Checkbox
              checked={exportOptions.includeStats}
              onChange={(e) => handleOptionChange('includeStats', e.target.checked)}
            >
              包含统计分析结果
            </Checkbox>
            <Checkbox
              checked={exportOptions.includeCharts}
              onChange={(e) => handleOptionChange('includeCharts', e.target.checked)}
            >
              包含图表
            </Checkbox>
          </Space>
        </Form.Item>

        {/* 图表类型选择 */}
        {exportOptions.includeCharts && (
          <Form.Item label="图表类型">
            <Checkbox.Group
              options={chartTypeOptions}
              value={exportOptions.chartTypes}
              onChange={(values) => handleOptionChange('chartTypes', values)}
            />
          </Form.Item>
        )}

        <Divider />

        {/* 自定义信息 */}
        <Form.Item label="自定义标题">
          <Input
            placeholder="输入导出文件的自定义标题"
            value={exportOptions.customTitle}
            onChange={(e) => handleOptionChange('customTitle', e.target.value)}
          />
        </Form.Item>

        <Form.Item label="描述信息">
          <TextArea
            rows={3}
            placeholder="输入导出文件的描述信息"
            value={exportOptions.customDescription}
            onChange={(e) => handleOptionChange('customDescription', e.target.value)}
          />
        </Form.Item>

        <Divider />

        {/* 导出按钮 */}
        <Form.Item>
          <Space>
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={handleExport}
              loading={loading}
              disabled={!selectedDataset}
              size="large"
            >
              开始导出
            </Button>
            <Button
              onClick={() => {
                setExportOptions({
                  format: 'csv',
                  includeCharts: true,
                  includeStats: true,
                  includeRawData: true,
                  chartTypes: ['bar', 'line', 'pie'],
                });
                setSelectedDataset('');
              }}
            >
              重置选项
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default ExportPanel;