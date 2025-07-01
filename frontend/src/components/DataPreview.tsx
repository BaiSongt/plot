import React, { useState, useEffect } from 'react';
import { Modal, Table, Spin, Alert, Statistic, Row, Col, Card } from 'antd';
import { useDataManager } from '../hooks/useDataManager';

interface DataPreviewProps {
  datasetId: string;
  visible: boolean;
  onClose: () => void;
}

interface PreviewData {
  columns: string[];
  rows: any[][];
  totalRows: number;
  summary: {
    [key: string]: {
      type: string;
      uniqueValues?: number;
      nullCount?: number;
      mean?: number;
      min?: number;
      max?: number;
    };
  };
}

/**
 * 数据预览组件
 * 显示数据集的前几行数据和基本统计信息
 */
const DataPreview: React.FC<DataPreviewProps> = ({ datasetId, visible, onClose }) => {
  const { dataList } = useDataManager();
  const [loading, setLoading] = useState(false);
  const [previewData, setPreviewData] = useState<PreviewData | null>(null);
  const [error, setError] = useState<string>('');

  const dataset = dataList.find(d => d.id === datasetId);

  // 获取预览数据
  const fetchPreviewData = async () => {
    if (!datasetId) return;

    setLoading(true);
    setError('');
    
    try {
      // 模拟API调用获取预览数据
      // 实际项目中这里应该调用后端API
      const response = await fetch(`/api/datasets/${datasetId}/preview`);
      
      if (!response.ok) {
        throw new Error('获取预览数据失败');
      }
      
      const data = await response.json();
      setPreviewData(data);
    } catch (err) {
      // 使用模拟数据作为备用
      console.warn('API不可用，使用模拟数据:', err);
      
      const mockData: PreviewData = {
        columns: dataset?.columns || ['列1', '列2', '列3', '列4'],
        rows: [
          ['数据1', 123, 45.6, '2024-01-01'],
          ['数据2', 456, 78.9, '2024-01-02'],
          ['数据3', 789, 12.3, '2024-01-03'],
          ['数据4', 234, 56.7, '2024-01-04'],
          ['数据5', 567, 89.0, '2024-01-05'],
        ],
        totalRows: dataset?.rows || 1000,
        summary: {
          '列1': { type: 'string', uniqueValues: 5, nullCount: 0 },
          '列2': { type: 'number', mean: 433.8, min: 123, max: 789, nullCount: 0 },
          '列3': { type: 'number', mean: 56.5, min: 12.3, max: 89.0, nullCount: 0 },
          '列4': { type: 'date', uniqueValues: 5, nullCount: 0 },
        },
      };
      
      setPreviewData(mockData);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (visible && datasetId) {
      fetchPreviewData();
    }
  }, [visible, datasetId]);

  // 构建表格列
  const tableColumns = previewData?.columns.map((col, index) => ({
    title: col,
    dataIndex: index,
    key: col,
    width: 150,
    ellipsis: true,
    render: (text: any) => {
      if (text === null || text === undefined) {
        return <span style={{ color: '#ccc', fontStyle: 'italic' }}>null</span>;
      }
      return String(text);
    },
  })) || [];

  // 构建表格数据
  const tableData = previewData?.rows.map((row, index) => {
    const rowData: any = { key: index };
    row.forEach((cell, cellIndex) => {
      rowData[cellIndex] = cell;
    });
    return rowData;
  }) || [];

  return (
    <Modal
      title={`数据预览 - ${dataset?.filename || '未知文件'}`}
      open={visible}
      onCancel={onClose}
      footer={null}
      width={1000}
      style={{ top: 20 }}
    >
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <Spin size="large" />
          <p style={{ marginTop: '16px' }}>加载数据中...</p>
        </div>
      ) : error ? (
        <Alert
          message="加载失败"
          description={error}
          type="error"
          showIcon
        />
      ) : previewData ? (
        <div>
          {/* 数据集基本信息 */}
          <Row gutter={16} style={{ marginBottom: '16px' }}>
            <Col span={6}>
              <Statistic title="总行数" value={previewData.totalRows} />
            </Col>
            <Col span={6}>
              <Statistic title="列数" value={previewData.columns.length} />
            </Col>
            <Col span={6}>
              <Statistic title="文件大小" value={dataset?.size || 0} suffix="KB" />
            </Col>
            <Col span={6}>
              <Statistic title="上传时间" value={dataset?.uploadTime || ''} />
            </Col>
          </Row>

          {/* 列统计信息 */}
          <Card title="列统计信息" size="small" style={{ marginBottom: '16px' }}>
            <Row gutter={[16, 16]}>
              {Object.entries(previewData.summary).map(([colName, stats]) => (
                <Col span={6} key={colName}>
                  <Card size="small" title={colName}>
                    <p><strong>类型:</strong> {stats.type}</p>
                    {stats.uniqueValues !== undefined && (
                      <p><strong>唯一值:</strong> {stats.uniqueValues}</p>
                    )}
                    {stats.nullCount !== undefined && (
                      <p><strong>空值:</strong> {stats.nullCount}</p>
                    )}
                    {stats.mean !== undefined && (
                      <p><strong>均值:</strong> {stats.mean.toFixed(2)}</p>
                    )}
                    {stats.min !== undefined && stats.max !== undefined && (
                      <p><strong>范围:</strong> {stats.min} - {stats.max}</p>
                    )}
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>

          {/* 数据预览表格 */}
          <Card title="数据预览（前5行）" size="small">
            <Table
              columns={tableColumns}
              dataSource={tableData}
              pagination={false}
              scroll={{ x: true, y: 300 }}
              size="small"
              bordered
            />
          </Card>
        </div>
      ) : null}
    </Modal>
  );
};

export default DataPreview;