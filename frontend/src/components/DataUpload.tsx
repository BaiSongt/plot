import React, { useState } from 'react';
import { Upload, Button, message, Card, Table, Space, Typography } from 'antd';
import { UploadOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';
import type { UploadProps, UploadFile } from 'antd';

const { Title, Text } = Typography;

interface DataUploadProps {
  onDataUploaded?: (data: any) => void;
}

interface DatasetInfo {
  id: string;
  name: string;
  size: number;
  uploadTime: string;
  rows: number;
  columns: number;
  status: 'success' | 'processing' | 'error';
}

const DataUpload: React.FC<DataUploadProps> = ({ onDataUploaded }) => {
  const [uploading, setUploading] = useState(false);
  const [datasets, setDatasets] = useState<DatasetInfo[]>([]);
  const [previewData, setPreviewData] = useState<any>(null);
  const [previewVisible, setPreviewVisible] = useState(false);

  const uploadProps: UploadProps = {
    name: 'file',
    action: '/api/datasets/upload',
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('token'),
    },
    accept: '.csv,.json,.xlsx,.xls',
    showUploadList: false,
    beforeUpload: (file) => {
      const isValidType = file.type === 'text/csv' || 
                         file.type === 'application/json' ||
                         file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
                         file.type === 'application/vnd.ms-excel';
      
      if (!isValidType) {
        message.error('只支持 CSV, JSON, Excel 文件格式!');
        return false;
      }
      
      const isLt10M = file.size / 1024 / 1024 < 10;
      if (!isLt10M) {
        message.error('文件大小不能超过 10MB!');
        return false;
      }
      
      return true;
    },
    onChange: (info) => {
      if (info.file.status === 'uploading') {
        setUploading(true);
      }
      
      if (info.file.status === 'done') {
        setUploading(false);
        message.success(`${info.file.name} 文件上传成功`);
        
        // 添加到数据集列表
        const newDataset: DatasetInfo = {
          id: info.file.response?.id || Date.now().toString(),
          name: info.file.name,
          size: info.file.size || 0,
          uploadTime: new Date().toLocaleString(),
          rows: info.file.response?.rows || 0,
          columns: info.file.response?.columns || 0,
          status: 'success'
        };
        
        setDatasets(prev => [newDataset, ...prev]);
        
        if (onDataUploaded) {
          onDataUploaded(info.file.response);
        }
      }
      
      if (info.file.status === 'error') {
        setUploading(false);
        message.error(`${info.file.name} 文件上传失败`);
      }
    },
  };

  const handlePreview = async (dataset: DatasetInfo) => {
    try {
      const response = await fetch(`/api/datasets/${dataset.id}/preview`, {
        headers: {
          'Authorization': 'Bearer ' + localStorage.getItem('token'),
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setPreviewData(data);
        setPreviewVisible(true);
      } else {
        message.error('预览数据失败');
      }
    } catch (error) {
      message.error('预览数据失败');
    }
  };

  const handleDelete = async (dataset: DatasetInfo) => {
    try {
      const response = await fetch(`/api/datasets/${dataset.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': 'Bearer ' + localStorage.getItem('token'),
        },
      });
      
      if (response.ok) {
        setDatasets(prev => prev.filter(d => d.id !== dataset.id));
        message.success('数据集删除成功');
      } else {
        message.error('删除数据集失败');
      }
    } catch (error) {
      message.error('删除数据集失败');
    }
  };

  const columns = [
    {
      title: '数据集名称',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
    },
    {
      title: '大小',
      dataIndex: 'size',
      key: 'size',
      render: (size: number) => {
        if (size < 1024) return `${size} B`;
        if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
        return `${(size / 1024 / 1024).toFixed(1)} MB`;
      },
    },
    {
      title: '行数',
      dataIndex: 'rows',
      key: 'rows',
    },
    {
      title: '列数',
      dataIndex: 'columns',
      key: 'columns',
    },
    {
      title: '上传时间',
      dataIndex: 'uploadTime',
      key: 'uploadTime',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusMap = {
          success: { color: '#52c41a', text: '成功' },
          processing: { color: '#1890ff', text: '处理中' },
          error: { color: '#ff4d4f', text: '错误' }
        };
        const config = statusMap[status as keyof typeof statusMap];
        return <Text style={{ color: config.color }}>{config.text}</Text>;
      },
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record: DatasetInfo) => (
        <Space size="middle">
          <Button 
            type="link" 
            icon={<EyeOutlined />} 
            onClick={() => handlePreview(record)}
          >
            预览
          </Button>
          <Button 
            type="link" 
            danger 
            icon={<DeleteOutlined />} 
            onClick={() => handleDelete(record)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>数据管理</Title>
      
      <Card title="上传数据" style={{ marginBottom: '24px' }}>
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <Upload {...uploadProps}>
            <Button 
              icon={<UploadOutlined />} 
              loading={uploading}
              size="large"
            >
              {uploading ? '上传中...' : '选择文件上传'}
            </Button>
          </Upload>
          <div style={{ marginTop: '16px', color: '#666' }}>
            <Text type="secondary">
              支持 CSV, JSON, Excel 格式，文件大小不超过 10MB
            </Text>
          </div>
        </div>
      </Card>

      <Card title="数据集列表">
        <Table 
          columns={columns} 
          dataSource={datasets}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 个数据集`,
          }}
        />
      </Card>

      {/* 数据预览模态框 */}
      {previewVisible && previewData && (
        <Card 
          title="数据预览" 
          style={{ 
            position: 'fixed', 
            top: '50px', 
            left: '50px', 
            right: '50px', 
            bottom: '50px', 
            zIndex: 1000,
            overflow: 'auto'
          }}
          extra={
            <Button onClick={() => setPreviewVisible(false)}>
              关闭
            </Button>
          }
        >
          <Table 
            dataSource={previewData.data || []}
            columns={(previewData.columns || []).map((col: string) => ({
              title: col,
              dataIndex: col,
              key: col,
              ellipsis: true,
            }))}
            pagination={{ pageSize: 20 }}
            scroll={{ x: true }}
          />
        </Card>
      )}
    </div>
  );
};

export default DataUpload;