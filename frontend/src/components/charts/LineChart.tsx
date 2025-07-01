import React from 'react';
import BaseChart from './BaseChart';
import type { EChartsOption } from 'echarts';
import type { ChartData, ChartOptions } from '@/types/chart';

interface LineChartProps extends ChartOptions {
  /** 图表数据 */
  data: ChartData[];
  /** X轴数据 */
  xAxisData?: (string | number)[];
  /** 是否平滑曲线 */
  smooth?: boolean;
  /** 是否显示区域填充 */
  areaStyle?: boolean | object;
  /** 是否显示标记点 */
  showSymbol?: boolean;
  /** 是否堆叠 */
  stack?: string | boolean;
  /** 自定义配置 */
  options?: EChartsOption;
}

/**
 * 折线图组件
 */
const LineChart: React.FC<LineChartProps> = ({
  data,
  xAxisData,
  smooth = true,
  areaStyle = false,
  showSymbol = true,
  stack = false,
  options = {},
  ...rest
}) => {
  // 处理区域填充样式
  const getAreaStyle = () => {
    if (areaStyle === false) return {};
    if (typeof areaStyle === 'boolean' && areaStyle) {
      return {
        areaStyle: {
          opacity: 0.3,
        },
      };
    }
    return { areaStyle: areaStyle };
  };

  // 构建系列数据
  const buildSeries = () => {
    if (!data || data.length === 0) return [];

    return [
      {
        name: rest.title || '数据',
        type: 'line',
        data: data.map((item) => item.value),
        smooth,
        showSymbol,
        stack,
        ...getAreaStyle(),
        itemStyle: {
          color: data[0]?.itemStyle?.color,
        },
        lineStyle: {
          width: 2,
        },
        emphasis: {
          focus: 'series',
          itemStyle: {
            borderWidth: 2,
            borderColor: '#fff',
          },
        },
      },
    ];
  };

  // 构建X轴配置
  const buildXAxis = () => {
    if (xAxisData && xAxisData.length > 0) {
      return {
        type: 'category',
        data: xAxisData,
        axisLine: {
          lineStyle: {
            color: '#d9d9d9',
          },
        },
        axisLabel: {
          color: '#666',
        },
      };
    }
    return {};
  };

  // 构建Y轴配置
  const buildYAxis = () => ({
    type: 'value',
    axisLine: {
      show: true,
      lineStyle: {
        color: '#d9d9d9',
      },
    },
    splitLine: {
      lineStyle: {
        type: 'dashed',
        color: '#f0f0f0',
      },
    },
    axisLabel: {
      color: '#666',
    },
  });

  // 合并配置
  const chartOptions: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'line',
      },
      formatter: (params: any) => {
        const title = params[0].axisValue || '';
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
      bottom: '10%',
      top: '15%',
      containLabel: true,
    },
    xAxis: buildXAxis(),
    yAxis: buildYAxis(),
    series: buildSeries() as any,
    ...options,
  };

  return <BaseChart type="line" data={data} options={chartOptions} {...rest} />;
};

export default LineChart;
