declare module '@/components/charts' {
  import { FC } from 'react';
  import { ChartData, ChartOptions } from '@/types/chart';

  export interface Scatter3DProps extends ChartOptions {
    data: Array<{
      x: number;
      y: number;
      z: number;
      value?: number;
      name?: string;
      series?: string;
      color?: string | number | any;
    }>;
    pointSize?: number;
    showAxes?: boolean;
    showGrid?: boolean;
    animate?: boolean;
    animationSpeed?: number;
    onPointClick?: (point: any) => void;
    style?: React.CSSProperties;
  }

  export const Scatter3D: FC<Scatter3DProps>;
  
  // 其他图表组件的类型声明可以在这里添加
  
  // 3D场景组件
  export interface SceneProps {
    showAxes?: boolean;
    showGrid?: boolean;
    cameraPosition?: [number, number, number];
    enableOrbitControls?: boolean;
    enableDamping?: boolean;
    dampingFactor?: number;
    autoRotate?: boolean;
    autoRotateSpeed?: number;
    style?: React.CSSProperties;
    children?: React.ReactNode;
  }
  
  export const Scene: FC<SceneProps>;
}

declare module '@/types/chart' {
  export interface ChartData {
    name?: string;
    value?: any;
    [key: string]: any;
  }

  export interface ChartOptions {
    title?: string;
    width?: number | string;
    height?: number | string;
    theme?: string | object;
    [key: string]: any;
  }

  export interface ChartSize {
    width: number;
    height: number;
  }

  export interface ResponsiveOption {
    breakpoint: number;
    option: object;
  }

  export interface ChartTheme {
    colors?: string[];
    fontFamily?: string;
    [key: string]: any;
  }


  export interface TooltipConfig {
    show?: boolean;
    formatter?: (params: any) => string;
    [key: string]: any;
  }
}
