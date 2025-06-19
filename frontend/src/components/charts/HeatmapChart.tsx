import React from 'react';
import BaseChart from './BaseChart';
import { EChartsOption } from 'echarts';
import { ChartData, ChartOptions } from '@/types/chart';

interface HeatmapData extends ChartData {
  /** X轴值 */
  x: string | number;
  /** Y轴值 */
  y: string | number;
  /** 值 */
  value: number;
  /** 自定义样式 */
  itemStyle?: {
    color?: string;
    [key: string]: any;
  };
}

interface HeatmapChartProps extends ChartOptions {
  /** 热力图数据 */
  data: HeatmapData[];
  /** X轴数据 */
  xAxisData?: (string | number)[];
  /** Y轴数据 */
  yAxisData?: (string | number)[];
  /** 是否显示数值标签 */
  showLabel?: boolean;
  /** 是否显示视觉映射组件 */
  visualMap?: boolean | {
    min?: number;
    max?: number;
    inRange?: {
      color: string[];
    };
    [key: string]: any;
  };
  /** 自定义配置 */
  options?: EChartsOption;
}

/**
 * 热力图组件
 */
const HeatmapChart: React.FC<HeatmapChartProps> = ({
  data,
  xAxisData,
  yAxisData,
  showLabel = true,
  visualMap = true,
  options = {},
  ...rest
}) => {
  // 准备热力图数据
  const prepareHeatmapData = () => {
    if (!data || data.length === 0) return [];

    // 如果没有提供xAxisData和yAxisData，则从数据中提取
    const uniqueXValues = Array.from(new Set(data.map((item) => item.x)));
    const uniqueYValues = Array.from(new Set(data.map((item) => item.y)));

    const xData = xAxisData || uniqueXValues;
    const yData = yAxisData || uniqueYValues;

    // 创建热力图数据
    const heatmapData: any[] = [];
    const dataMap = new Map();

    // 创建数据映射，方便查找
    data.forEach((item) => {
      const key = `${item.x}-${item.y}`;
      dataMap.set(key, item.value);
    });

    // 填充热力图数据
    yData.forEach((y, yIndex) => {
      xData.forEach((x, xIndex) => {
        const value = dataMap.get(`${x}-${y}`) || 0;
        heatmapData.push([xIndex, yIndex, value]);
      });
    });

    return {
      xData,
      yData,
      heatmapData,
    };
  };

  // 构建视觉映射配置
  const buildVisualMap = () => {
    if (visualMap === false) return {};

    const defaultVisualMap = {
      min: 0,
      max: Math.max(...data.map((item) => item.value), 10),
      inRange: {
        color: ['#f0f0f0', '#1890ff'],
      },
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0%',
    };

    if (typeof visualMap === 'boolean') {
      return {
        visualMap: defaultVisualMap,
      };
    }

    return {
      visualMap: {
        ...defaultVisualMap,
        ...visualMap,
      },
    };
  };

  // 构建X轴配置
  const buildXAxis = (xData: (string | number)[]) => ({
    type: 'category',
    data: xData,
    splitArea: {
      show: true,
    },
    axisLabel: {
      color: '#666',
    },
    axisLine: {
      lineStyle: {
        color: '#d9d9d9',
      },
    },
  });

  // 构建Y轴配置
  const buildYAxis = (yData: (string | number)[]) => ({
    type: 'category',
    data: yData,
    splitArea: {
      show: true,
    },
    axisLabel: {
      color: '#666',
    },
    axisLine: {
      lineStyle: {
        color: '#d9d9d9',
      },
    },
  });

  // 构建系列配置
  const buildSeries = (xData: (string | number)[], yData: (string | number)[], heatmapData: any[]) => ({
    name: rest.title || '热力图',
    type: 'heatmap',
    data: heatmapData,
    label: {
      show: showLabel,
      formatter: (params: any) => {
        const value = params.data[2];
        return value === 0 ? '' : value;
      },
    },
    emphasis: {
      itemStyle: {
        shadowBlur: 10,
        shadowColor: 'rgba(0, 0, 0, 0.5)',
      },
    },
    progressive: 1000,
    animation: false,
  });

  // 准备数据和配置
  const { xData, yData, heatmapData } = prepareHeatmapData();

  // 合并配置
  const chartOptions: EChartsOption = {
    tooltip: {
      position: 'top',
      formatter: (params: any) => {
        const xIndex = params.data[0];
        const yIndex = params.data[1];
        const value = params.data[2];
        
        return `${xData[xIndex]} / ${yData[yIndex]}: ${value}`;
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '10%',
      containLabel: true,
    },
    xAxis: buildXAxis(xData),
    yAxis: buildYAxis(yData),
    series: [buildSeries(xData, yData, heatmapData) as any],
    ...buildVisualMap(),
    ...options,
  };

  return <BaseChart type="heatmap" data={data} options={chartOptions} {...rest} />;
};

export default HeatmapChart;
