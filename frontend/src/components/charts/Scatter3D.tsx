import React, { useRef, useMemo, useCallback } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, Point } from '@react-three/drei';
import * as THREE from 'three';
import Scene from './three/Scene';
import type { ChartData, ChartOptions } from '../../types/chart';

interface Scatter3DData extends ChartData {
  /** X轴值 */
  x: number;
  /** Y轴值 */
  y: number;
  /** Z轴值 */
  z: number;
  /** 点的大小 */
  size?: number;
  /** 点的颜色 */
  color?: string | number | THREE.Color;
  /** 点的透明度 */
  opacity?: number;
}

interface Scatter3DProps extends ChartOptions {
  /** 3D散点图数据 */
  data: Scatter3DData[];
  /** X轴名称 */
  xAxisName?: string;
  /** Y轴名称 */
  yAxisName?: string;
  /** Z轴名称 */
  zAxisName?: string;
  /** 点的大小 */
  pointSize?: number;
  /** 是否显示坐标轴 */
  showAxes?: boolean;
  /** 是否显示网格 */
  showGrid?: boolean;
  /** 是否显示图例 */
  showLegend?: boolean;
  /** 是否启用动画 */
  animate?: boolean;
  /** 动画速度 */
  animationSpeed?: number;
  /** 自定义配置 */
  options?: any;
}

/**
 * 3D散点图组件
 */
const Scatter3D: React.FC<Scatter3DProps> = ({
  data,
  xAxisName = 'X',
  yAxisName = 'Y',
  zAxisName = 'Z',
  pointSize = 0.1,
  showAxes = true,
  showGrid = true,
  showLegend = true,
  animate = true,
  animationSpeed = 1,
  options = {},
  ...rest
}) => {
  // 准备点数据
  const points = useMemo(() => {
    if (!data || data.length === 0) return [];

    return data.map((item) => ({
      position: [item.x, item.y, item.z] as [number, number, number],
      color: item.color || '#1890ff',
      size: item.size || pointSize,
      opacity: item.opacity || 1,
      userData: {
        name: item.name,
        value: item.value,
        x: item.x,
        y: item.y,
        z: item.z,
      },
    }));
  }, [data, pointSize]);

  // 计算数据范围
  const { xRange, yRange, zRange } = useMemo(() => {
    if (!data || data.length === 0) {
      return { xRange: [0, 10], yRange: [0, 10], zRange: [0, 10] };
    }

    const xValues = data.map((item) => item.x);
    const yValues = data.map((item) => item.y);
    const zValues = data.map((item) => item.z);

    const xMin = Math.min(...xValues);
    const xMax = Math.max(...xValues);
    const yMin = Math.min(...yValues);
    const yMax = Math.max(...yValues);
    const zMin = Math.min(...zValues);
    const zMax = Math.max(...zValues);

    // 添加一些边距
    const xPadding = (xMax - xMin) * 0.1;
    const yPadding = (yMax - yMin) * 0.1;
    const zPadding = (zMax - zMin) * 0.1;

    return {
      xRange: [xMin - xPadding, xMax + xPadding],
      yRange: [yMin - yPadding, yMax + yPadding],
      zRange: [zMin - zPadding, zMax + zPadding],
    };
  }, [data]);

  // 计算相机初始位置
  const cameraPosition: [number, number, number] = useMemo(() => {
    const xRangeSize = xRange[1] - xRange[0];
    const yRangeSize = yRange[1] - yRange[0];
    const zRangeSize = zRange[1] - zRange[0];

    const maxRange = Math.max(xRangeSize, yRangeSize, zRangeSize);
    return [maxRange * 1.5, maxRange * 1.5, maxRange * 1.5];
  }, [xRange, yRange, zRange]);

  // 渲染坐标轴标签
  const renderAxisLabels = () => {
    const labelStyle: React.CSSProperties = {
      position: 'absolute',
      color: '#333',
      fontSize: '12px',
      fontWeight: 'bold',
      pointerEvents: 'none',
    };

    return (
      <>
        {/* X轴标签 */}
        <div
          style={{
            ...labelStyle,
            left: '50%',
            bottom: '20px',
            transform: 'translateX(-50%)',
          }}
        >
          {xAxisName}
        </div>

        {/* Y轴标签 */}
        <div
          style={{
            ...labelStyle,
            left: '20px',
            top: '50%',
            transform: 'translateY(-50%) rotate(-90deg)',
            transformOrigin: 'left center',
          }}
        >
          {yAxisName}
        </div>

        {/* Z轴标签 */}
        <div
          style={{
            ...labelStyle,
            top: '20px',
            right: '20px',
          }}
        >
          {zAxisName}
        </div>
      </>
    );
  };

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <Scene
        cameraPosition={cameraPosition}
        showAxes={showAxes}
        showGrid={showGrid}
        {...rest}
      >
        {/* 3D点云 */}
        <Points>
          <pointsMaterial
            size={pointSize}
            sizeAttenuation
            vertexColors
            transparent
            opacity={1}
            alphaTest={0.01}
          />
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              count={points.length}
              array={new Float32Array(points.flatMap((p) => p.position))}
              itemSize={3}
            />
            <bufferAttribute
              attach="attributes-color"
              count={points.length}
              array={new Float32Array(
                points.flatMap((p) => {
                  const color = new THREE.Color(p.color);
                  return [color.r, color.g, color.b];
                })
              )}
              itemSize={3}
            />
            <bufferAttribute
              attach="attributes-size"
              count={points.length}
              array={new Float32Array(points.map((p) => p.size || pointSize))}
              itemSize={1}
            />
            <bufferAttribute
              attach="attributes-opacity"
              count={points.length}
              array={new Float32Array(points.map((p) => p.opacity || 1))}
              itemSize={1}
            />
          </bufferGeometry>
        </Points>

        {/* 坐标轴辅助对象 */}
        {showAxes && (
          <group>
            <axesHelper args={[Math.max(...xRange, ...yRange, ...zRange) * 1.2]} />
            <gridHelper
              args={[Math.max(xRange[1] - xRange[0], yRange[1] - yRange[0], zRange[1] - zRange[0]) * 1.5, 10]}
              rotation={[Math.PI / 2, 0, 0]}
            >
              <meshBasicMaterial color="#cccccc" side={THREE.DoubleSide} />
            </gridHelper>
          </group>
        )}
      </Scene>

      {/* 坐标轴标签 */}
      {showAxes && renderAxisLabels()}

      {/* 图例 */}
      {showLegend && (
        <div
          style={{
            position: 'absolute',
            bottom: '20px',
            right: '20px',
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            padding: '8px 12px',
            borderRadius: '4px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
          }}
        >
          <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>图例</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {Array.from(new Set(data.map((item) => item.name))).map((name) => (
              <div key={name} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div
                  style={{
                    width: '12px',
                    height: '12px',
                    borderRadius: '50%',
                    backgroundColor: '#1890ff',
                  }}
                />
                <span>{name}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Scatter3D;
