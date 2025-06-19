// 导出 3D 场景组件
export { default as Scene } from './Scene';

// 导出 3D 图表组件
export { default as Scatter3D } from './Scatter3D';

// 导出 3D 工具函数
export * from './utils';

// 导出类型
export * from '@/types/chart3d';

// 导出 React Three Fiber 组件
export * from '@react-three/fiber';
export * from '@react-three/drei';
export * from '@react-three/postprocessing';

// 重新导出 Three.js 常用模块
export * as THREE from 'three';
export { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
export { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer';
export { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass';
export { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass';

// 导出工具函数
export * from '@/utils/chart3dUtils';
