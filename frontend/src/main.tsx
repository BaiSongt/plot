import React, { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { ConfigProvider, theme } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import 'antd/dist/reset.css';
import './index.css';
import './App.css';
import App from './App';

// 设置主题配置
const themeConfig = {
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 6,
    colorInfo: '#1890ff',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#ff4d4f',
    colorLink: '#1890ff',
    fontSize: 14,
    fontSizeSM: 12,
    fontSizeLG: 16,
    padding: 16,
    margin: 16,
    marginXXS: 4,
    marginXS: 8,
    marginSM: 12,
    marginMD: 16,
    marginLG: 24,
    marginXL: 32,
    marginXXL: 48,
    paddingXS: 8,
    paddingSM: 12,
    paddingMD: 16,
    paddingLG: 24,
    paddingXL: 32,
  },
  components: {
    Button: {
      defaultBorderColor: '#d9d9d9',
      defaultColor: 'rgba(0, 0, 0, 0.88)',
      defaultBg: '#ffffff',
      borderRadius: 6,
      colorPrimary: '#1890ff',
      colorError: '#ff4d4f',
      colorWarning: '#faad14',
      colorSuccess: '#52c41a',
    },
    Card: {
      paddingLG: 24,
    },
    Menu: {
      itemSelectedColor: '#1890ff',
      itemSelectedBg: '#e6f7ff',
      itemHoverColor: '#1890ff',
      itemHoverBg: 'rgba(24, 144, 255, 0.06)',
      itemActiveBg: '#e6f7ff',
    },
  },
  algorithm: theme.defaultAlgorithm,
};

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ConfigProvider
      locale={zhCN}
      theme={themeConfig}
      getPopupContainer={(triggerNode) => triggerNode?.parentElement || document.body}
    >
      <App />
    </ConfigProvider>
  </StrictMode>
);
