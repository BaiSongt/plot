import React, { useMemo, useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Text } from '@react-three/drei';
import { EffectComposer, Bloom, SSAO } from '@react-three/postprocessing';
import { Surface3DConfig, Point3D } from '@/types/chart3d';
import { computeBoundingBox, createColorAttribute } from '@/utils/chart3dUtils';

// 默认配置
const defaultConfig: Surface3DConfig = {
  // 场景设置
  backgroundColor: 0x111111,
  fogColor: 0x000000,
  fogDensity: 0.05,
  
  // 表面设置
  width: 10,
  height: 10,
  widthSegments: 50,
  heightSegments: 50,
  
  // 颜色设置
  color: 0x2194ce,
  opacity: 0.8,
  wireframe: false,
  wireframeLinewidth: 1,
  wireframeColor: 0x444444,
  
  // 材质设置
  materialType: 'standard',
  materialShininess: 30,
  materialRoughness: 0.5,
  materialMetalness: 0.1,
  materialEmissive: 0x000000,
  materialEmissiveIntensity: 0.1,
  
  // 辅助对象
  showAxes: true,
  axesLength: 10,
  showGrid: true,
  gridSize: 10,
  gridDivisions: 10,
  
  // 控制器设置
  enableOrbitControls: true,
  enableDamping: true,
  dampingFactor: 0.05,
  autoRotate: false,
  autoRotateSpeed: 1.0,
  minDistance: 1,
  maxDistance: 1000,
  minPolarAngle: 0,
  maxPolarAngle: Math.PI,
  enableZoom: true,
  zoomSpeed: 1.0,
  enablePan: true,
  panSpeed: 0.8,
  screenSpacePanning: true,
  enableRotate: true,
  rotateSpeed: 0.8,
  enableKeys: true,
  keyPanSpeed: 7.0,
  
  // 标签设置
  showLabels: true,
  xLabel: 'X',
  yLabel: 'Y',
  zLabel: 'Z',
  labelColor: 0xffffff,
  labelSize: 0.5,
  
  // 工具提示
  showTooltip: true,
  
  // 动画设置
  animate: false,
  animationDuration: 2000,
  
  // 事件回调
  onClick: undefined,
  onHover: undefined,
  onLoad: undefined,
  onError: undefined,
};

// 表面图组件
interface Surface3DProps {
  data: number[][] | ((x: number, z: number) => number);
  config?: Partial<Surface3DConfig>;
  style?: React.CSSProperties;
  className?: string;
  onLoad?: () => void;
  onError?: (error: Error) => void;
  onClick?: (point: Point3D | null, event: any) => void;
  onHover?: (point: Point3D | null, event: any) => void;
}

const Surface3D: React.FC<Surface3DProps> = ({
  data,
  config: userConfig,
  style,
  className,
  onLoad,
  onError,
  onClick,
  onHover,
}) => {
  // 合并配置
  const config = useMemo(() => ({
    ...defaultConfig,
    ...userConfig,
  }), [userConfig]);
  
  // 生成表面几何体
  const { geometry, points } = useMemo(() => {
    try {
      const width = config.width || 10;
      const height = config.height || 10;
      const widthSegments = config.widthSegments || 50;
      const heightSegments = config.heightSegments || 50;
      
      // 创建平面几何体
      const geometry = new THREE.PlaneGeometry(width, height, widthSegments - 1, heightSegments - 1);
      
      // 获取顶点数组
      const positions = geometry.attributes.position.array as Float32Array;
      const points: Point3D[] = [];
      
      // 更新顶点高度
      for (let i = 0; i <= widthSegments; i++) {
        for (let j = 0; j <= heightSegments; j++) {
          const index = (i * (heightSegments + 1) + j) * 3;
          const x = (i / widthSegments - 0.5) * width;
          const z = (j / heightSegments - 0.5) * height;
          
          // 计算高度值
          let y = 0;
          if (typeof data === 'function') {
            y = data(x, z);
          } else if (Array.isArray(data) && data[i] && typeof data[i][j] === 'number') {
            y = data[i][j];
          }
          
          // 更新顶点位置
          positions[index + 1] = y;
          
          // 存储点数据
          points.push({
            x,
            y,
            z,
            value: y,
            index: points.length,
            u: i / widthSegments,
            v: j / heightSegments,
          });
        }
      }
      
      // 更新法线以支持光照
      geometry.computeVertexNormals();
      
      return { geometry, points };
    } catch (error) {
      console.error('Error creating surface geometry:', error);
      if (onError) onError(error as Error);
      return { geometry: new THREE.BufferGeometry(), points: [] };
    }
  }, [data, config, onError]);
  
  // 计算边界框
  const boundingBox = useMemo(() => {
    return computeBoundingBox(points);
  }, [points]);
  
  // 创建材质
  const material = useMemo(() => {
    const materialOptions: THREE.MaterialParameters = {
      color: config.color,
      transparent: true,
      opacity: config.opacity,
      wireframe: config.wireframe,
      wireframeLinewidth: config.wireframeLinewidth,
      wireframeLinecap: 'round',
      wireframeLinejoin: 'round',
    };
    
    // 根据配置选择材质类型
    switch (config.materialType) {
      case 'basic':
        return new THREE.MeshBasicMaterial(materialOptions);
      case 'lambert':
        return new THREE.MeshLambertMaterial(materialOptions);
      case 'phong':
        return new THREE.MeshPhongMaterial({
          ...materialOptions,
          shininess: config.materialShininess,
        });
      case 'standard':
        return new THREE.MeshStandardMaterial({
          ...materialOptions,
          roughness: config.materialRoughness,
          metalness: config.materialMetalness,
          emissive: config.materialEmissive,
          emissiveIntensity: config.materialEmissiveIntensity,
        });
      case 'physical':
        return new THREE.MeshPhysicalMaterial({
          ...materialOptions,
          roughness: config.materialRoughness,
          metalness: config.materialMetalness,
          emissive: config.materialEmissive,
          emissiveIntensity: config.materialEmissiveIntensity,
          clearcoat: 0.1,
          clearcoatRoughness: 0.1,
        });
      case 'toon':
        return new THREE.MeshToonMaterial(materialOptions);
      default:
        return new THREE.MeshStandardMaterial(materialOptions);
    }
  }, [config]);
  
  // 处理点击事件
  const handleClick = useCallback((event: any) => {
    if (!onClick) return;
    
    // 获取点击的坐标
    const { point, face } = event;
    if (!face) {
      onClick(null, event);
      return;
    }
    
    // 查找最近的点
    const clickedPoint = findClosestPoint(point, points);
    onClick(clickedPoint, event);
  }, [onClick, points]);
  
  // 处理悬停事件
  const handlePointerMove = useCallback((event: any) => {
    if (!onHover) return;
    
    const { point, face } = event;
    if (!face) {
      onHover(null, event);
      return;
    }
    
    // 查找最近的点
    const hoveredPoint = findClosestPoint(point, points);
    onHover(hoveredPoint, event);
  }, [onHover, points]);
  
  // 查找最近的点
  const findClosestPoint = (target: THREE.Vector3, points: Point3D[]): Point3D | null => {
    if (!points.length) return null;
    
    let closestPoint = points[0];
    let minDistance = Infinity;
    
    for (const point of points) {
      const distance = Math.sqrt(
        Math.pow(point.x - target.x, 2) +
        Math.pow(point.y - target.y, 2) +
        Math.pow(point.z - target.z, 2)
      );
      
      if (distance < minDistance) {
        minDistance = distance;
        closestPoint = point;
      }
    }
    
    return closestPoint;
  };
  
  // 渲染表面
  return (
    <div 
      className={`surface-3d-container ${className || ''}`} 
      style={{ width: '100%', height: '100%', ...style }}
    >
      <Canvas
        camera={{
          position: [0, 5, 10],
          fov: 50,
          near: 0.1,
          far: 1000,
        }}
        onCreated={({ gl, scene, camera }) => {
          // 设置渲染器
          gl.setPixelRatio(window.devicePixelRatio);
          gl.shadowMap.enabled = true;
          gl.shadowMap.type = THREE.PCFSoftShadowMap;
          
          // 设置场景
          scene.background = new THREE.Color(config.backgroundColor || 0x111111);
          scene.fog = new THREE.FogExp2(
            config.fogColor || 0x000000,
            config.fogDensity || 0.05
          );
          
          // 添加环境光
          const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
          scene.add(ambientLight);
          
          // 添加方向光
          const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
          directionalLight.position.set(5, 10, 7);
          directionalLight.castShadow = true;
          scene.add(directionalLight);
          
          // 添加半球光
          const hemisphereLight = new THREE.HemisphereLight(0x4488aa, 0x002244, 0.2);
          scene.add(hemisphereLight);
          
          // 加载完成回调
          if (onLoad) onLoad();
        }}
      >
        {/* 表面网格 */}
        <mesh
          geometry={geometry}
          material={material}
          rotation={[-Math.PI / 2, 0, 0]}
          onClick={handleClick}
          onPointerMove={handlePointerMove}
          castShadow
          receiveShadow
        >
          {config.wireframe && (
            <meshBasicMaterial 
              color={config.wireframeColor} 
              wireframe 
              opacity={0.3}
              transparent
            />
          )}
        </mesh>
        
        {/* 坐标轴 */}
        {config.showAxes && (
          <axesHelper args={[config.axesLength || 10]} />
        )}
        
        {/* 网格 */}
        {config.showGrid && (
          <gridHelper 
            args={[config.gridSize || 10, config.gridDivisions || 10]} 
            rotation={[0, 0, 0]}
          />
        )}
        
        {/* 坐标轴标签 */}
        {config.showLabels && (
          <>
            <Text
              position={[config.gridSize ? config.gridSize / 2 + 1 : 6, 0, 0]}
              fontSize={config.labelSize || 0.5}
              color={config.labelColor}
              anchorX="center"
              anchorY="middle"
            >
              {config.xLabel || 'X'}
            </Text>
            <Text
              position={[0, (config.gridSize ? config.gridSize / 2 : 5) + 1, 0]}
              fontSize={config.labelSize || 0.5}
              color={config.labelColor}
              anchorX="center"
              anchorY="middle"
            >
              {config.yLabel || 'Y'}
            </Text>
            <Text
              position={[0, 0, (config.gridSize ? config.gridSize / 2 : 5) + 1]}
              fontSize={config.labelSize || 0.5}
              color={config.labelColor}
              anchorX="center"
              anchorY="middle"
            >
              {config.zLabel || 'Z'}
            </Text>
          </>
        )}
        
        {/* 轨道控制器 */}
        {config.enableOrbitControls && (
          <OrbitControls
            enableDamping={config.enableDamping}
            dampingFactor={config.dampingFactor}
            autoRotate={config.autoRotate}
            autoRotateSpeed={config.autoRotateSpeed}
            minDistance={config.minDistance}
            maxDistance={config.maxDistance}
            minPolarAngle={config.minPolarAngle}
            maxPolarAngle={config.maxPolarAngle}
            enableZoom={config.enableZoom}
            zoomSpeed={config.zoomSpeed}
            enablePan={config.enablePan}
            panSpeed={config.panSpeed}
            screenSpacePanning={config.screenSpacePanning}
            enableRotate={config.enableRotate}
            rotateSpeed={config.rotateSpeed}
            enableKeys={config.enableKeys}
            keyPanSpeed={config.keyPanSpeed}
          />
        )}
        
        {/* 后期处理 */}
        <EffectComposer>
          <SSAO />
          <Bloom
            intensity={1.5}
            kernelSize={2}
            luminanceThreshold={0.1}
            luminanceSmoothing={0.5}
          />
        </EffectComposer>
      </Canvas>
    </div>
  );
};

export default Surface3D;
