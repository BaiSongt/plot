/**
 * 基础图表数据类型
 */
export interface ChartData {
  /** 数据项名称 */
  name: string;
  /** 数据值 */
  value: number;
  /** 可选：数据项ID */
  id?: string | number;
  /** 可选：数据项分组 */
  group?: string;
  /** 可选：自定义样式 */
  itemStyle?: {
    color?: string;
    [key: string]: any;
  };
  [key: string]: any;
}

/**
 * 基础图表配置项
 */
export interface ChartOptions {
  /** 图表标题 */
  title?: string;
  /** 图表副标题 */
  subtext?: string;
  /** 图表宽度 */
  width?: number | string;
  /** 图表高度 */
  height?: number | string;
  /** 图表主题 */
  theme?: string;
  /** 是否显示加载动画 */
  showLoading?: boolean;
  /** 自定义样式 */
  style?: React.CSSProperties;
  /** 图表渲染完成回调 */
  onRendered?: () => void;
  /** 图表事件 */
  onEvents?: Record<string, (params: any) => void>;
}

/**
 * 图表尺寸
 */
export interface ChartSize {
  width: number | string;
  height: number | string;
}

/**
 * 图表响应式配置
 */
export interface ResponsiveOption {
  /** 满足的媒体查询条件 */
  query: {
    /** 最小宽度 */
    minWidth?: number;
    /** 最大宽度 */
    maxWidth?: number;
    /** 最小高度 */
    minHeight?: number;
    /** 最大高度 */
    maxHeight?: number;
  };
  /** 满足条件时的图表选项 */
  option: Partial<ChartOptions>;
}

/**
 * 图表主题配置
 */
export interface ChartTheme {
  /** 主题名称 */
  name: string;
  /** 主题配置 */
  theme: any;
}

/**
 * 图表工具提示配置
 */
export interface TooltipConfig {
  /** 是否显示 */
  show?: boolean;
  /** 触发类型 */
  trigger?: 'item' | 'axis' | 'none';
  /** 提示框内容格式器 */
  formatter?: string | ((params: any) => string);
  /** 提示框背景色 */
  backgroundColor?: string;
  /** 提示框边框颜色 */
  borderColor?: string;
  /** 提示框边框宽度 */
  borderWidth?: number;
  /** 提示框内边距 */
  padding?: number | number[];
  /** 提示框文本样式 */
  textStyle?: {
    color?: string;
    fontSize?: number;
    [key: string]: any;
  };
  /** 提示框位置 */
  position?: string | ((point: [number, number]) => [number, number]);
}
