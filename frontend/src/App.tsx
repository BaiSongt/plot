import React from 'react';
import './App.css';

function App() {
  return (
    <div style={{ padding: '20px', backgroundColor: '#f0f2f5', minHeight: '100vh' }}>
      <h1 style={{ color: '#1890ff' }}>数据可视化平台</h1>
      <p>欢迎使用数据可视化平台！</p>
      <div style={{ 
        backgroundColor: 'white', 
        padding: '20px', 
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        <h2>系统状态</h2>
        <p>✅ React 应用正常运行</p>
        <p>✅ 样式加载正常</p>
        <p>✅ 组件渲染正常</p>
      </div>
    </div>
  );
}

export default App;
