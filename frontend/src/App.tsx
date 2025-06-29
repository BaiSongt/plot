import React, { useState } from 'react';
import { Layout, Menu, Upload, Button, Card, Table, message } from 'antd';
import {
  UploadOutlined,
  BarChartOutlined,
  LineChartOutlined,
  PieChartOutlined,
  DotChartOutlined,
  SettingOutlined,
  UserOutlined
} from '@ant-design/icons';
import type { MenuProps, UploadProps } from 'antd';
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
  getItem('用户设置', 'settings', <SettingOutlined />),
];

function App() {
  const [collapsed, setCollapsed] = useState(false);
  const [selectedKey, setSelectedKey] = useState('upload');
  const [dataList, setDataList] = useState<any[]>([]);

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

  // 获取数据列表
  const fetchDataList = async () => {
    try {
      // 暂时使用模拟数据，后续连接真实API
      const mockData = [
        {
          key: '1',
          filename: 'sample_data.csv',
          size: '2.5 MB',
          uploadTime: '2024-01-15 10:30:00',
          status: '已处理'
        }
      ];
      setDataList(mockData);
    } catch (error) {
      message.error('获取数据列表失败');
    }
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
              dataSource={dataList}
              columns={[
                { title: '文件名', dataIndex: 'filename', key: 'filename' },
                { title: '大小', dataIndex: 'size', key: 'size' },
                { title: '上传时间', dataIndex: 'uploadTime', key: 'uploadTime' },
                { title: '状态', dataIndex: 'status', key: 'status' },
              ]}
              pagination={{ pageSize: 10 }}
            />
          </Card>
        );
      case 'bar':
        return (
          <Card title="柱状图" style={{ margin: '16px' }}>
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <BarChartOutlined style={{ fontSize: '48px', color: '#1890ff' }} />
              <p>柱状图组件开发中...</p>
            </div>
          </Card>
        );
      case 'line':
        return (
          <Card title="折线图" style={{ margin: '16px' }}>
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <LineChartOutlined style={{ fontSize: '48px', color: '#1890ff' }} />
              <p>折线图组件开发中...</p>
            </div>
          </Card>
        );
      case 'pie':
        return (
          <Card title="饼图" style={{ margin: '16px' }}>
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <PieChartOutlined style={{ fontSize: '48px', color: '#1890ff' }} />
              <p>饼图组件开发中...</p>
            </div>
          </Card>
        );
      case 'scatter':
        return (
          <Card title="散点图" style={{ margin: '16px' }}>
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <DotChartOutlined style={{ fontSize: '48px', color: '#1890ff' }} />
              <p>散点图组件开发中...</p>
            </div>
          </Card>
        );
      case 'scatter3d':
        return (
          <Card title="3D散点图" style={{ margin: '16px' }}>
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <DotChartOutlined style={{ fontSize: '48px', color: '#1890ff' }} />
              <p>3D散点图组件开发中...</p>
            </div>
          </Card>
        );
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
    </Layout>
  );
}

export default App;
