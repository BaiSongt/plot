import React, { useState, useMemo } from 'react';
import { Scatter3D } from '@/components/charts';
import { Card, Slider, Switch, Space, Typography } from 'antd';

const { Title, Paragraph } = Typography;

// 生成随机数据
const generateRandomData = (count: number, seriesCount: number) => {
  const series = [];
  const seriesColors = ['#ff4d4f', '#1890ff', '#52c41a', '#faad14', '#722ed1'];
  
  for (let s = 0; s < seriesCount; s++) {
    for (let i = 0; i < count; i++) {
      const x = Math.random() * 10 - 5;
      const y = Math.random() * 10 - 5;
      const z = Math.sin(Math.sqrt(x * x + y * y)) + Math.random() * 0.5;
      
      series.push({
        x,
        y,
        z,
        value: Math.abs(z) * 10,
        name: `系列 ${s + 1}`,
        series: `series-${s}`,
        color: seriesColors[s % seriesColors.length],
      });
    }
  }
  
  return series;
};

const Scatter3DExample: React.FC = () => {
  // 状态管理
  const [pointCount, setPointCount] = useState<number>(100);
  const [seriesCount, setSeriesCount] = useState<number>(3);
  const [pointSize, setPointSize] = useState<number>(0.2);
  const [showAxes, setShowAxes] = useState<boolean>(true);
  const [showGrid, setShowGrid] = useState<boolean>(true);
  const [animate, setAnimate] = useState<boolean>(true);
  const [animationSpeed, setAnimationSpeed] = useState<number>(1);
  
  // 生成数据
  const chartData = useMemo(() => {
    return generateRandomData(pointCount, seriesCount);
  }, [pointCount, seriesCount]);
  
  // 处理点点击事件
  const handlePointClick = (point: any) => {
    console.log('点击点:', point);
  };
  
  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>3D 散点图示例</Title>
      <Paragraph>这是一个使用 Three.js 和 React Three Fiber 创建的 3D 散点图组件。</Paragraph>
      
      <Card title="控制面板" style={{ marginBottom: '24px' }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <div>数据点数量: {pointCount}</div>
            <Slider
              min={10}
              max={500}
              step={10}
              value={pointCount}
              onChange={setPointCount}
              style={{ width: '100%' }}
            />
          </div>
          
          <div>
            <div>数据系列: {seriesCount}</div>
            <Slider
              min={1}
              max={5}
              step={1}
              value={seriesCount}
              onChange={setSeriesCount}
              style={{ width: '100%' }}
            />
          </div>
          
          <div>
            <div>点大小: {pointSize.toFixed(1)}</div>
            <Slider
              min={0.1}
              max={1}
              step={0.1}
              value={pointSize}
              onChange={setPointSize}
              style={{ width: '100%' }}
            />
          </div>
          
          <Space>
            <Switch checked={showAxes} onChange={setShowAxes} />
            <span>显示坐标轴</span>
            
            <Switch checked={showGrid} onChange={setShowGrid} style={{ marginLeft: '16px' }} />
            <span>显示网格</span>
            
            <Switch checked={animate} onChange={setAnimate} style={{ marginLeft: '16px' }} />
            <span>启用动画</span>
          </Space>
          
          <div>
            <div>动画速度: {animationSpeed.toFixed(1)}x</div>
            <Slider
              min={0.1}
              max={5}
              step={0.1}
              value={animationSpeed}
              onChange={setAnimationSpeed}
              style={{ width: '100%' }}
              disabled={!animate}
            />
          </div>
        </Space>
      </Card>
      
      <Card title="3D 散点图" style={{ height: '600px' }}>
        <Scatter3D
          data={chartData}
          pointSize={pointSize}
          showAxes={showAxes}
          showGrid={showGrid}
          animate={animate}
          animationSpeed={animationSpeed}
          onPointClick={handlePointClick}
          style={{ width: '100%', height: '100%' }}
        />
      </Card>
    </div>
  );
};

export default Scatter3DExample;
