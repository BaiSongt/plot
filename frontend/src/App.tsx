import React, { useState } from 'react';
import { Layout, Menu, Upload, Button, Card, Table, message, Space, Popconfirm } from 'antd';
import {
  UploadOutlined,
  BarChartOutlined,
  LineChartOutlined,
  PieChartOutlined,
  DotChartOutlined,
  SettingOutlined,
  UserOutlined,
  DeleteOutlined,
  EyeOutlined,
  FunctionOutlined,
  DownloadOutlined
} from '@ant-design/icons';
import type { MenuProps, UploadProps } from 'antd';
import ChartContainer from './components/ChartContainer';
import AnalysisPanel from './components/AnalysisPanel';
import DataPreview from './components/DataPreview';
import ExportPanel from './components/ExportPanel';
import { useDataManager } from './hooks/useDataManager';
import './App.css';

const { Header, Sider, Content } = Layout;

type MenuItem = Required<MenuProps>['items'][number];

function getItem(
  label: React.ReactNode,
  key: React.Key,
  icon?: React.ReactNode,
  children?: MenuItem[],
): MenuItem {
  return {
    key,
    icon,
    children,
    label,
  } as MenuItem;
}

const menuItems: MenuItem[] = [
  getItem('数据管理', 'data', <UploadOutlined />, [
    getItem('数据上传', 'upload'),
    getItem('数据列表', 'list'),
  ]),
  getItem('图表分析', 'charts', <BarChartOutlined />, [
    getItem('柱状图', 'bar'),
    getItem('折线图', 'line'),
    getItem('饼图', 'pie'),
    getItem('散点图', 'scatter'),
    getItem('3D散点图', 'scatter3d'),
  ]),
  getItem('数据分析', 'analysis', <FunctionOutlined />),
  getItem('数据导出', 'export', <DownloadOutlined />),
  getItem('用户设置', 'settings', <SettingOutlined />),
];

function App() {
  const [collapsed, setCollapsed] = useState(false);
  const [selectedKey, setSelectedKey] = useState('upload');
  const [previewVisible, setPreviewVisible] = useState(false);
  const [previewDatasetId, setPreviewDatasetId] = useState<string>('');
  const { dataList, loading, fetchDataList, deleteDataset } = useDataManager();

  const uploadProps: UploadProps = {
    name: 'file',
    action: 'http://localhost:8000/api/v1/datasets/upload-test',
    headers: {
      // 暂时不使用认证，后续会添加
    },
    data: {
      // 可以添加额外的表单数据
    },
    accept: '.csv,.json,.xlsx,.xls',
    onChange(info) {
      if (info.file.status !== 'uploading') {
        console.log(info.file, info.fileList);
      }
      if (info.file.status === 'done') {
        message.success(`${info.file.name} 文件上传成功`);
        // 刷新数据列表
        fetchDataList();
      } else if (info.file.status === 'error') {
        message.error(`${info.file.name} 文件上传失败: ${info.file.response?.detail || '未知错误'}`);
      }
    },
    beforeUpload(file) {
      const isValidType = file.type === 'text/csv' ||
                         file.type === 'application/json' ||
                         file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
                         file.type === 'application/vnd.ms-excel';

      if (!isValidType) {
        message.error('只支持 CSV, JSON, Excel 格式文件!');
        return false;
      }

      const isLt10M = file.size / 1024 / 1024 < 10;
      if (!isLt10M) {
        message.error('文件大小不能超过 10MB!');
        return false;
      }

      return true;
    },
  };

  // 处理数据集删除
  const handleDeleteDataset = async (datasetId: string) => {
    await deleteDataset(datasetId);
    message.success('数据集删除成功');
  };

  const handlePreviewDataset = (id: string) => {
    setPreviewDatasetId(id);
    setPreviewVisible(true);
  };

  const handleClosePreview = () => {
    setPreviewVisible(false);
    setPreviewDatasetId('');
  };

  const renderContent = () => {
    switch (selectedKey) {
      case 'upload':
        return (
          <Card title="数据上传" style={{ margin: '16px' }}>
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <Upload {...uploadProps}>
                <Button icon={<UploadOutlined />} size="large">
                  点击上传数据文件
                </Button>
              </Upload>
              <p style={{ marginTop: '16px', color: '#666' }}>
                支持 CSV, JSON, Excel 格式文件
              </p>
            </div>
          </Card>
        );
      case 'list':
        return (
          <Card title="数据列表" style={{ margin: '16px' }}>
            <Table
              dataSource={dataList.map(item => ({ ...item, key: item.id }))}
              loading={loading}
              columns={[
                { title: '文件名', dataIndex: 'filename', key: 'filename' },
                { title: '大小', dataIndex: 'size', key: 'size' },
                { title: '上传时间', dataIndex: 'uploadTime', key: 'uploadTime' },
                { title: '状态', dataIndex: 'status', key: 'status' },
                { 
                  title: '列数', 
                  dataIndex: 'columns', 
                  key: 'columns',
                  render: (columns: string[]) => columns?.length || '-'
                },
                { 
                  title: '行数', 
                  dataIndex: 'rowCount', 
                  key: 'rowCount',
                  render: (count: number) => count || '-'
                },
                {
                  title: '操作',
                  key: 'action',
                  render: (_, record) => (
                    <Space size="middle">
                      <Button
                        type="link"
                        icon={<EyeOutlined />}
                        onClick={() => handlePreviewDataset(record.id)}
                      >
                        预览
                      </Button>
                      <Popconfirm
                        title="确定要删除这个数据集吗？"
                        onConfirm={() => handleDeleteDataset(record.id)}
                        okText="确定"
                        cancelText="取消"
                      >
                        <Button
                          type="link"
                          danger
                          icon={<DeleteOutlined />}
                        >
                          删除
                        </Button>
                      </Popconfirm>
                    </Space>
                  ),
                },
              ]}
              pagination={{ pageSize: 10 }}
            />
          </Card>
        );
      case 'bar':
        return <ChartContainer chartType="bar" title="柱状图分析" />;
      case 'line':
        return <ChartContainer chartType="line" title="趋势分析" />;
      case 'pie':
        return <ChartContainer chartType="pie" title="比例分析" />;
      case 'scatter':
        return <ChartContainer chartType="scatter" title="相关性分析" />;
      case 'scatter3d':
        return <ChartContainer chartType="scatter3d" title="3D数据分析" />;
      case 'analysis':
        return <AnalysisPanel />;
      case 'export':
        return <ExportPanel />;
      case 'settings':
        return (
          <Card title="用户设置" style={{ margin: '16px' }}>
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <UserOutlined style={{ fontSize: '48px', color: '#1890ff' }} />
              <p>用户设置功能开发中...</p>
            </div>
          </Card>
        );
      default:
        return (
          <Card title="欢迎使用" style={{ margin: '16px' }}>
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <h2>数据可视化平台</h2>
              <p>请从左侧菜单选择功能</p>
            </div>
          </Card>
        );
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        theme="light"
      >
        <div style={{
          height: '64px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderBottom: '1px solid #f0f0f0'
        }}>
          <h3 style={{ margin: 0, color: '#1890ff' }}>
            {collapsed ? 'DV' : '数据可视化'}
          </h3>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onClick={({ key }) => setSelectedKey(key as string)}
        />
      </Sider>
      <Layout>
        <Header style={{
          padding: '0 16px',
          background: '#fff',
          borderBottom: '1px solid #f0f0f0',
          display: 'flex',
          alignItems: 'center'
        }}>
          <h2 style={{ margin: 0, color: '#1890ff' }}>数据可视化平台</h2>
        </Header>
        <Content style={{ background: '#f0f2f5' }}>
          {renderContent()}
        </Content>
      </Layout>
      
      {/* 数据预览模态框 */}
      <DataPreview
        datasetId={previewDatasetId}
        visible={previewVisible}
        onClose={handleClosePreview}
      />
    </Layout>
  );
};

export default App;
