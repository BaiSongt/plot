import React from 'react';
import BaseChart from './BaseChart';
import { EChartsOption } from 'echarts';
import { ChartData, ChartOptions } from '@/types/chart';

interface BarChartProps extends ChartOptions {
  /** 图表数据 */
  data: ChartData[];
  /** X轴数据 */
  xAxisData?: (string | number)[];
  /** 是否水平显示 */
  horizontal?: boolean;
  /** 是否显示图例 */
  showLegend?: boolean;
  /** 是否显示数据标签 */
  showLabel?: boolean;
  /** 柱状图宽度 */
  barWidth?: number | string;
  /** 柱状图圆角 */
  barBorderRadius?: number | [number, number, number, number];
  /** 是否堆叠 */
  stack?: string | boolean;
  /** 自定义配置 */
  options?: EChartsOption;
}

/**
 * 柱状图组件
 */
const BarChart: React.FC<BarChartProps> = ({
  data,
  xAxisData,
  horizontal = false,
  showLegend = true,
  showLabel = false,
  barWidth = '60%',
  barBorderRadius = 0,
  stack = false,
  options = {},
  ...rest
}) => {
  // 构建系列数据
  const buildSeries = () => {
    if (!data || data.length === 0) return [];

    return [
      {
        name: rest.title || '数据',
        type: 'bar',
        data: data.map((item) => ({
          value: item.value,
          itemStyle: item.itemStyle,
        })),
        barWidth,
        barGap: '30%',
        barCategoryGap: '40%',
        itemStyle: {
          borderRadius: barBorderRadius,
          color: (params: any) => {
            // 如果数据项有自定义颜色，则使用自定义颜色
            if (data[params.dataIndex]?.itemStyle?.color) {
              return data[params.dataIndex].itemStyle?.color;
            }
            // 否则使用默认颜色
            return new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(24, 144, 255, 0.85)' },
              { offset: 1, color: 'rgba(24, 144, 255, 0.1)' },
            ]);
          },
        },
        label: showLabel
          ? {
              show: true,
              position: 'top',
              formatter: '{c}',
              color: '#666',
            }
          : undefined,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.3)',
          },
        },
        stack,
      },
    ];
  };

  // 构建X轴配置
  const buildXAxis = () => {
    const baseAxis = {
      type: horizontal ? 'value' : 'category',
      data: horizontal ? undefined : xAxisData || data.map((item) => item.name),
      axisLine: {
        lineStyle: {
          color: '#d9d9d9',
        },
      },
      axisLabel: {
        color: '#666',
      },
      axisTick: {
        alignWithLabel: true,
      },
    };

    if (horizontal) {
      return {
        ...baseAxis,
        splitLine: {
          lineStyle: {
            type: 'dashed',
            color: '#f0f0f0',
          },
        },
      };
    }

    return baseAxis;
  };

  // 构建Y轴配置
  const buildYAxis = () => {
    const baseAxis = {
      type: horizontal ? 'category' : 'value',
      data: horizontal ? data.map((item) => item.name) : undefined,
      axisLine: {
        show: true,
        lineStyle: {
          color: '#d9d9d9',
        },
      },
      axisLabel: {
        color: '#666',
      },
    };

    if (!horizontal) {
      return {
        ...baseAxis,
        splitLine: {
          lineStyle: {
            type: 'dashed',
            color: '#f0f0f0',
          },
        },
      };
    }

    return baseAxis;
  };

  // 构建图例配置
  const buildLegend = () => {
    if (!showLegend) return {};

    return {
      legend: {
        data: [rest.title || '数据'],
        bottom: 0,
        textStyle: {
          color: '#666',
        },
      },
    };
  };

  // 合并配置
  const chartOptions: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
      formatter: (params: any) => {
        const title = horizontal ? params[0].name : params[0].axisValue;
        const items = params
          .map(
            (item: any) =>
              `<div style="margin: 5px 0;">
                <span style="display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:${item.color};"></span>
                ${item.seriesName}: <strong>${item.value}</strong>
              </div>`
          )
          .join('');
        return `<div>
          <div>${title}</div>
          ${items}
        </div>`;
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: showLegend ? '15%' : '3%',
      top: '10%',
      containLabel: true,
    },
    xAxis: buildXAxis(),
    yAxis: buildYAxis(),
    ...buildLegend(),
    series: buildSeries() as any,
    ...options,
  };

  return <BaseChart type="bar" data={data} options={chartOptions} {...rest} />;
};

export default BarChart;
