# 3D 可视化组件

这个目录包含了基于 Three.js 和 React Three Fiber 的 3D 数据可视化组件。

## 组件列表

### Scene

一个可重用的 3D 场景组件，封装了 Three.js 的基本设置。

#### 属性

| 属性名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `width` | `number` | `window.innerWidth` | 场景宽度 |
| `height` | `number` | `window.innerHeight` | 场景高度 |
| `cameraPosition` | `[number, number, number]` | `[0, 0, 10]` | 相机位置 |
| `lookAt` | `[number, number, number]` | `[0, 0, 0]` | 相机看向的点 |
| `fov` | `number` | `75` | 视野角度 |
| `near` | `number` | `0.1` | 近裁剪面 |
| `far` | `number` | `1000` | 远裁剪面 |
| `clearColor` | `number \| string` | `0x111111` | 背景色 |
| `showAxes` | `boolean` | `true` | 是否显示坐标轴 |
| `axesSize` | `number` | `5` | 坐标轴大小 |
| `showGrid` | `boolean` | `true` | 是否显示网格 |
| `gridSize` | `number` | `10` | 网格大小 |
| `gridDivisions` | `number` | `10` | 网格分割数 |
| `enableOrbitControls` | `boolean` | `true` | 是否启用轨道控制 |
| `enableDamping` | `boolean` | `true` | 是否启用阻尼效果 |
| `dampingFactor` | `number` | `0.05` | 阻尼系数 |
| `autoRotate` | `boolean` | `false` | 是否自动旋转 |
| `autoRotateSpeed` | `number` | `1.0` | 自动旋转速度 |
| `onLoad` | `() => void` | - | 场景加载完成回调 |
| `onError` | `(error: Error) => void` | - | 错误处理回调 |
| `style` | `React.CSSProperties` | - | 容器样式 |
| `className` | `string` | - | 容器类名 |
| `children` | `React.ReactNode` | - | 子组件 |

### Scatter3D

3D 散点图组件，用于展示三维数据点。

#### 属性

| 属性名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `data` | `Point3D[]` | `[]` | 数据点数组 |
| `width` | `number` | `800` | 图表宽度 |
| `height` | `number` | `600` | 图表高度 |
| `pointSize` | `number` | `0.2` | 点大小 |
| `showAxes` | `boolean` | `true` | 是否显示坐标轴 |
| `showGrid` | `boolean` | `true` | 是否显示网格 |
| `animate` | `boolean` | `true` | 是否启用动画 |
| `animationSpeed` | `number` | `1.0` | 动画速度 |
| `onPointClick` | `(point: Point3D) => void` | - | 点击数据点回调 |
| `onPointHover` | `(point: Point3D \| null) => void` | - | 悬停数据点回调 |
| `style` | `React.CSSProperties` | - | 容器样式 |
| `className` | `string` | - | 容器类名 |

## 使用示例

```tsx
import React, { useState } from 'react';
import { Scatter3D } from './Scatter3D';
import { generateScatterData } from '../../../utils/chart3dUtils';

const Scatter3DExample = () => {
  const [data] = useState(() => generateScatterData(100, 3));
  
  const handlePointClick = (point) => {
    console.log('Clicked point:', point);
  };
  
  const handlePointHover = (point) => {
    // 处理悬停逻辑
  };
  
  return (
    <div style={{ width: '100%', height: '600px' }}>
      <Scatter3D
        data={data}
        pointSize={0.3}
        showAxes={true}
        showGrid={true}
        animate={true}
        animationSpeed={1.5}
        onPointClick={handlePointClick}
        onPointHover={handlePointHover}
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  );
};

export default Scatter3DExample;
```

## 依赖

- three
- @react-three/fiber
- @react-three/drei
- @react-three/postprocessing

## 开发指南

### 添加新组件

1. 在 `src/components/charts/three` 目录下创建新组件
2. 在 `index.ts` 中导出新组件
3. 更新此文档

### 样式指南

- 使用 TypeScript 进行类型检查
- 遵循 React 函数组件和 Hooks 最佳实践
- 组件应尽量保持无状态，通过 props 控制行为
- 使用 `styled-components` 或 CSS Modules 处理样式

## 许可证

MIT
