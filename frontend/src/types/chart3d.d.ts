import * as THREE from 'three';

declare module 'three' {
  interface Object3D {
    // 添加自定义属性
    userData: {
      [key: string]: any;
    };
  }
}

// 3D 点数据类型
export interface Point3D {
  x: number;
  y: number;
  z: number;
  value?: number;
  name?: string;
  series?: string;
  color?: string | number | THREE.Color;
  [key: string]: any;
}

// 3D 场景配置
export interface Scene3DConfig {
  // 场景设置
  backgroundColor?: number | string;
  fogColor?: number | string;
  fogDensity?: number;
  
  // 环境光
  ambientLightColor?: number;
  ambientLightIntensity?: number;
  
  // 方向光
  directionalLightColor?: number;
  directionalLightIntensity?: number;
  directionalLightPosition?: [number, number, number];
  
  // 半球光
  hemisphereLightSkyColor?: number;
  hemisphereLightGroundColor?: number;
  hemisphereLightIntensity?: number;
  
  // 辅助对象
  showAxesHelper?: boolean;
  axesHelperSize?: number;
  showGridHelper?: boolean;
  gridHelperSize?: number;
  gridDivisions?: number;
  
  // 控制器设置
  enableOrbitControls?: boolean;
  enableDamping?: boolean;
  dampingFactor?: number;
  autoRotate?: boolean;
  autoRotateSpeed?: number;
  minDistance?: number;
  maxDistance?: number;
  minPolarAngle?: number;
  maxPolarAngle?: number;
  enableZoom?: boolean;
  zoomSpeed?: number;
  enablePan?: boolean;
  panSpeed?: number;
  screenSpacePanning?: boolean;
  enableRotate?: boolean;
  rotateSpeed?: number;
  enableKeys?: boolean;
  keyPanSpeed?: number;
}

// 3D 散点图配置
export interface Scatter3DConfig extends Scene3DConfig {
  // 点设置
  pointSize?: number;
  pointSizeScale?: number;
  minPointSize?: number;
  maxPointSize?: number;
  pointColor?: string | number | THREE.Color;
  pointOpacity?: number;
  pointShape?: 'circle' | 'square' | 'diamond' | 'triangle' | 'star';
  
  // 动画设置
  enableAnimation?: boolean;
  animationDuration?: number;
  animationEasing?: (t: number) => number;
  
  // 交互设置
  enableHover?: boolean;
  hoverSizeMultiplier?: number;
  hoverColor?: string | number | THREE.Color;
  enableSelection?: boolean;
  selectionColor?: string | number | THREE.Color;
  
  // 标签设置
  showLabels?: boolean;
  labelField?: string;
  labelColor?: string;
  labelBackgroundColor?: string;
  labelFontSize?: number;
  labelOffset?: [number, number, number];
  
  // 图例设置
  showLegend?: boolean;
  legendPosition?: 'top' | 'right' | 'bottom' | 'left';
  legendTitle?: string;
  
  // 坐标轴设置
  showXAxis?: boolean;
  showYAxis?: boolean;
  showZAxis?: boolean;
  axisColor?: string | number;
  axisWidth?: number;
  showAxisLabels?: boolean;
  xAxisLabel?: string;
  yAxisLabel?: string;
  zAxisLabel?: string;
  labelColor?: string | number;
  labelFontSize?: number;
  showTicks?: boolean;
  tickSize?: number;
  tickColor?: string | number;
  showTickLabels?: boolean;
  tickLabelColor?: string | number;
  tickLabelFontSize?: number;
  tickFormat?: (value: number) => string;
  
  // 网格设置
  showGrid?: boolean;
  gridColor?: string | number;
  gridOpacity?: number;
  gridWidth?: number;
  
  // 相机设置
  cameraPosition?: [number, number, number];
  cameraLookAt?: [number, number, number];
  cameraFov?: number;
  cameraNear?: number;
  cameraFar?: number;
  
  // 渲染设置
  antialias?: boolean;
  alpha?: boolean;
  clearColor?: number | string;
  clearAlpha?: number;
  pixelRatio?: number;
  shadowMapEnabled?: boolean;
  shadowMapType?: THREE.ShadowMapType;
  
  // 事件回调
  onPointClick?: (point: Point3D, event: MouseEvent) => void;
  onPointHover?: (point: Point3D | null, event: MouseEvent) => void;
  onPointSelect?: (point: Point3D | null, event: MouseEvent) => void;
  onLoad?: () => void;
  onError?: (error: Error) => void;
  
  // 自定义渲染
  rendererExtensions?: any[];
  customRender?: (renderer: THREE.WebGLRenderer, scene: THREE.Scene, camera: THREE.Camera) => void;
  customSceneSetup?: (scene: THREE.Scene) => void;
  customCameraSetup?: (camera: THREE.Camera) => void;
  customControlsSetup?: (controls: any) => void;
  
  // 性能优化
  useInstancing?: boolean;
  maxPoints?: number;
  levelOfDetail?: 'low' | 'medium' | 'high';
  
  // 调试
  stats?: boolean;
  showBoundingBox?: boolean;
  showNormals?: boolean;
  showWireframe?: boolean;
}

// 3D 表面图配置
export interface Surface3DConfig extends Scene3DConfig {
  // 表面设置
  width?: number;
  height?: number;
  widthSegments?: number;
  heightSegments?: number;
  
  // 颜色设置
  color?: string | number | THREE.Color | ((point: Point3D) => string | number | THREE.Color);
  opacity?: number;
  wireframe?: boolean;
  wireframeLinewidth?: number;
  wireframeColor?: string | number | THREE.Color;
  
  // 光照设置
  materialType?: 'basic' | 'standard' | 'phong' | 'lambert' | 'toon' | 'physical';
  materialShininess?: number;
  materialRoughness?: number;
  materialMetalness?: number;
  materialEmissive?: string | number | THREE.Color;
  materialEmissiveIntensity?: number;
  
  // 动画设置
  animate?: boolean;
  animationDuration?: number;
  animationEasing?: (t: number) => number;
  
  // 交互设置
  enableRotation?: boolean;
  enableZoom?: boolean;
  enablePan?: boolean;
  
  // 坐标轴和网格设置
  showAxes?: boolean;
  axesLength?: number;
  showGrid?: boolean;
  gridSize?: number;
  gridDivisions?: number;
  
  // 标签设置
  showLabels?: boolean;
  xLabel?: string;
  yLabel?: string;
  zLabel?: string;
  labelColor?: string | number;
  labelSize?: number;
  
  // 工具提示
  showTooltip?: boolean;
  tooltipFormatter?: (point: Point3D) => string;
  
  // 事件回调
  onClick?: (point: Point3D | null, event: MouseEvent) => void;
  onHover?: (point: Point3D | null, event: MouseEvent) => void;
  onLoad?: () => void;
  onError?: (error: Error) => void;
}
