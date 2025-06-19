import React, { useState } from 'react';
import { Layout, Menu, theme, Typography, Space } from 'antd';
import { AppstoreOutlined, BarChartOutlined, LineChartOutlined, PieChartOutlined } from '@ant-design/icons';
import './App.css';

// 导入图表组件
import Scatter3DExample from './examples/Scatter3DExample';

const { Header, Content, Sider } = Layout;
const { Title } = Typography;

// 定义页面类型
type PageType = 'dashboard' | 'scatter3d' | 'line' | 'bar' | 'pie';

function App() {
  const [collapsed, setCollapsed] = useState(false);
  const [currentPage, setCurrentPage] = useState<PageType>('scatter3d');
  
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  // 渲染当前页面内容
  const renderContent = () => {
    switch (currentPage) {
      case 'scatter3d':
        return <Scatter3DExample />;
      case 'dashboard':
      default:
        return (
          <div style={{ padding: 24, minHeight: 360, background: colorBgContainer, borderRadius: borderRadiusLG }}>
            <Title level={3}>数据可视化平台</Title>
            <p>欢迎使用数据可视化平台，请从左侧菜单选择图表类型。</p>
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
          defaultSelectedKeys={['scatter3d']}
          mode="inline"
          items={[
            {
              key: 'dashboard',
              icon: <AppstoreOutlined />,
              label: '控制台',
              onClick: () => setCurrentPage('dashboard'),
            },
            {
              key: '3d',
              icon: <BarChartOutlined />,
              label: '3D 图表',
              children: [
                {
                  key: 'scatter3d',
                  label: '3D 散点图',
                  onClick: () => setCurrentPage('scatter3d'),
                },
                // 可以添加更多3D图表
              ],
            },
            {
              key: '2d',
              icon: <LineChartOutlined />,
              label: '2D 图表',
              children: [
                { key: 'line', label: '折线图' },
                { key: 'bar', label: '柱状图' },
                { key: 'pie', label: '饼图' },
              ],
            },
          ]}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: 0, background: colorBgContainer }}>
          <div style={{ padding: '0 24px' }}>
            <Title level={4} style={{ margin: '16px 0' }}>数据可视化平台</Title>
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
