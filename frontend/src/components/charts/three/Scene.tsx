import React, { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Stats, PerspectiveCamera, OrthographicCamera } from '@react-three/drei';
import * as THREE from 'three';
import { EffectComposer, Bloom, DepthOfField } from '@react-three/postprocessing';

interface SceneProps {
  /** 子元素 */
  children?: React.ReactNode;
  /** 是否显示状态面板 */
  showStats?: boolean;
  /** 是否显示坐标轴 */
  showAxes?: boolean;
  /** 是否显示网格 */
  showGrid?: boolean;
  /** 背景颜色 */
  backgroundColor?: string | number;
  /** 相机类型 */
  cameraType?: 'perspective' | 'orthographic';
  /** 相机位置 */
  cameraPosition?: [number, number, number];
  /** 是否启用轨道控制 */
  enableOrbitControls?: boolean;
  /** 是否启用阻尼效果 */
  enableDamping?: boolean;
  /** 阻尼系数 */
  dampingFactor?: number;
  /** 是否自动旋转 */
  autoRotate?: boolean;
  /** 自动旋转速度 */
  autoRotateSpeed?: number;
  /** 是否启用缩放 */
  enableZoom?: boolean;
  /** 是否启用旋转 */
  enableRotate?: boolean;
  /** 是否启用平移 */
  enablePan?: boolean;
  /** 最小距离 */
  minDistance?: number;
  /** 最大距离 */
  maxDistance?: number;
  /** 视场角 */
  fov?: number;
  /** 近平面 */
  near?: number;
  /** 远平面 */
  far?: number;
  /** 是否启用后期处理 */
  enablePostProcessing?: boolean;
  /** 自定义样式 */
  style?: React.CSSProperties;
  /** 场景加载完成回调 */
  onSceneReady?: (scene: THREE.Scene, camera: THREE.Camera, renderer: THREE.WebGLRenderer) => void;
}

/**
 * 3D场景组件
 */
const Scene: React.FC<SceneProps> = ({
  children,
  showStats = false,
  showAxes = true,
  showGrid = true,
  backgroundColor = '#f0f0f0',
  cameraType = 'perspective',
  cameraPosition = [5, 5, 5],
  enableOrbitControls = true,
  enableDamping = true,
  dampingFactor = 0.05,
  autoRotate = false,
  autoRotateSpeed = 1,
  enableZoom = true,
  enableRotate = true,
  enablePan = true,
  minDistance = 1,
  maxDistance = 1000,
  fov = 50,
  near = 0.1,
  far = 1000,
  enablePostProcessing = false,
  style = { width: '100%', height: '100%' },
  onSceneReady,
}) => {
  const sceneRef = useRef<THREE.Scene>(null);
  const cameraRef = useRef<THREE.Camera>(null);
  const rendererRef = useRef<THREE.WebGLRenderer>(null);
  const [isReady, setIsReady] = useState(false);

  // 场景初始化完成回调
  useEffect(() => {
    if (sceneRef.current && cameraRef.current && rendererRef.current) {
      onSceneReady?.(sceneRef.current, cameraRef.current, rendererRef.current);
      setIsReady(true);
    }
  }, [onSceneReady]);

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', ...style }}>
      <Canvas
        style={{ background: backgroundColor }}
        camera={{
          position: cameraPosition,
          fov,
          near,
          far,
        }}
        onCreated={({ gl, scene, camera }) => {
          sceneRef.current = scene;
          cameraRef.current = camera;
          rendererRef.current = gl;

          // 设置抗锯齿
          gl.setPixelRatio(window.devicePixelRatio);
          gl.shadowMap.enabled = true;
          gl.shadowMap.type = THREE.PCFSoftShadowMap;
        }}
      >
        {/* 环境光 */}
        <ambientLight intensity={0.5} />

        {/* 平行光 */}
        <directionalLight
          position={[10, 10, 5]}
          intensity={1}
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
          shadow-camera-near={0.5}
          shadow-camera-far={500}
        />

        {/* 坐标轴辅助 */}
        {showAxes && <axesHelper args={[5]} />}

        {/* 网格辅助 */}
        {showGrid && (
          <gridHelper args={[10, 10]}>
            <meshBasicMaterial color="#cccccc" side={THREE.DoubleSide} />
          </gridHelper>
        )}

        {/* 轨道控制器 */}
        {enableOrbitControls && (
          <OrbitControls
            enableDamping={enableDamping}
            dampingFactor={dampingFactor}
            autoRotate={autoRotate}
            autoRotateSpeed={autoRotateSpeed}
            enableZoom={enableZoom}
            enableRotate={enableRotate}
            enablePan={enablePan}
            minDistance={minDistance}
            maxDistance={maxDistance}
          />
        )}

        {/* 后期处理 */}
        {enablePostProcessing ? (
          <EffectComposer>
            <Bloom luminanceThreshold={0} luminanceSmoothing={0.9} height={300} />
            <DepthOfField focusDistance={0} focalLength={0.02} bokehScale={2} height={480} />
          </EffectComposer>
        ) : null}

        {/* 子元素 */}
        {children}
      </Canvas>

      {/* 状态面板 */}
      {showStats && <Stats className="stats-panel" />}
    </div>
  );
};

export default Scene;
