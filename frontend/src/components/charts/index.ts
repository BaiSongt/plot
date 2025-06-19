// 基础图表组件
export { default as BaseChart } from './BaseChart';

// 2D图表
export { default as LineChart } from './LineChart';
export { default as BarChart } from './BarChart';
export { default as PieChart } from './PieChart';
export { default as ScatterChart } from './ScatterChart';
export { default as HeatmapChart } from './HeatmapChart';

// 3D图表
export { default as Scatter3D } from './Scatter3D';

// 3D场景和工具
export { default as Scene } from './three/Scene';

// 导出类型
export type {
  ChartData,
  ChartOptions,
  ChartSize,
  ResponsiveOption,
  ChartTheme,
  TooltipConfig,
} from '@/types/chart';
