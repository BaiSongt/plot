import React, { useState, useEffect, useMemo } from 'react';
import { Layout, Menu, theme, Typography, Space, Button } from 'antd';
import { AppstoreOutlined, BarChartOutlined, LineChartOutlined, PieChartOutlined, LogoutOutlined, DatabaseOutlined } from '@ant-design/icons';
import './App.css';

// 导入组件
import Scatter3DExample from './examples/Scatter3DExample';
import Login from './components/Login';
import DataUpload from './components/DataUpload';

const { Header, Content, Sider } = Layout;
const { Title } = Typography;

// 定义页面类型
type PageType = 'dashboard' | 'data' | 'scatter3d' | 'line' | 'bar' | 'pie';

interface User {
  id: number;
  username: string;
  email: string;
}

function App() {
  const [collapsed, setCollapsed] = useState(false);
  const [currentPage, setCurrentPage] = useState<PageType>('dashboard');
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  // 检查用户登录状态
  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      try {
        setUser(JSON.parse(userData));
      } catch (error) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const handleLoginSuccess = (userData: User) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setCurrentPage('dashboard');
  };

  // 如果正在加载，显示加载状态
  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <Typography.Title level={3}>加载中...</Typography.Title>
      </div>
    );
  }

  // 如果用户未登录，显示登录页面
  if (!user) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  // 菜单项配置
  const menuItems = useMemo(() => [
    {
      key: 'dashboard',
      icon: <AppstoreOutlined />,
      label: '控制台',
    },
    {
      key: 'data',
      icon: <DatabaseOutlined />,
      label: '数据管理',
    },
    {
      key: '3d-charts',
      icon: <BarChartOutlined />,
      label: '3D图表',
      children: [
        {
          key: 'scatter3d',
          label: '3D散点图',
        },
      ],
    },
    {
      key: '2d-charts',
      icon: <LineChartOutlined />,
      label: '2D图表',
      children: [
        {
          key: 'line',
          label: '折线图',
        },
        {
          key: 'bar',
          label: '柱状图',
        },
        {
          key: 'pie',
          label: '饼图',
        },
      ],
    },
  ], []);

  // 渲染当前页面内容
  const renderContent = () => {
    switch (currentPage) {
      case 'dashboard':
        return (
          <div style={{ padding: '24px' }}>
            <Title level={2}>控制台</Title>
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <div>
                <Typography.Title level={4}>欢迎使用数据可视化平台</Typography.Title>
                <Typography.Paragraph>
                  这是一个功能强大的数据可视化平台，支持多种图表类型和数据分析功能。
                </Typography.Paragraph>
              </div>
              
              <div>
                <Typography.Title level={4}>快速开始</Typography.Title>
                <Typography.Paragraph>
                  1. 前往「数据管理」上传您的数据文件<br/>
                  2. 选择合适的图表类型进行可视化<br/>
                  3. 自定义图表样式和参数<br/>
                  4. 导出或分享您的可视化结果
                </Typography.Paragraph>
              </div>
              
              <div>
                <Typography.Title level={4}>支持的功能</Typography.Title>
                <ul>
                  <li>多种数据格式支持（CSV、JSON、Excel）</li>
                  <li>2D和3D图表可视化</li>
                  <li>交互式图表操作</li>
                  <li>实时数据更新</li>
                  <li>图表导出和分享</li>
                </ul>
              </div>
            </Space>
          </div>
        );
      case 'data':
        return <DataUpload />;
      case 'scatter3d':
        return <Scatter3DExample />;
      case 'line':
        return (
          <div style={{ padding: '24px' }}>
            <Title level={2}>折线图</Title>
            <p>折线图组件开发中...</p>
          </div>
        );
      case 'bar':
        return (
          <div style={{ padding: '24px' }}>
            <Title level={2}>柱状图</Title>
            <p>柱状图组件开发中...</p>
          </div>
        );
      case 'pie':
        return (
          <div style={{ padding: '24px' }}>
            <Title level={2}>饼图</Title>
            <p>饼图组件开发中...</p>
          </div>
        );
      default:
        return (
          <div style={{ padding: '24px' }}>
            <Title level={2}>控制台</Title>
            <p>欢迎使用数据可视化平台</p>
          </div>
        );
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={(value) => setCollapsed(value)}>
        <div className="demo-logo-vertical" />
        <Menu
          theme="dark"
          defaultSelectedKeys={['dashboard']}
          mode="inline"
          items={menuItems}
          onClick={({ key }) => setCurrentPage(key as PageType)}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: 0, background: colorBgContainer }}>
          <div style={{ 
            padding: '0 24px', 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center' 
          }}>
            <Title level={4} style={{ margin: '16px 0' }}>数据可视化平台</Title>
            <Space>
              <span>欢迎，{user.username}</span>
              <Button 
                type="text" 
                icon={<LogoutOutlined />} 
                onClick={handleLogout}
              >
                退出登录
              </Button>
            </Space>
          </div>
        </Header>
        <Content style={{ margin: '24px 16px 0' }}>
          {renderContent()}
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
