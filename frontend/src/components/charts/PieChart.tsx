import React from 'react';
import BaseChart from './BaseChart';
import type { EChartsOption } from 'echarts';
import type { ChartData, ChartOptions } from '@/types/chart';

interface PieChartProps extends ChartOptions {
  /** 图表数据 */
  data: ChartData[];
  /** 是否显示图例 */
  showLegend?: boolean;
  /** 是否显示标签 */
  showLabel?: boolean;
  /** 是否显示标签线 */
  showLabelLine?: boolean;
  /** 是否显示中心文字 */
  showCenterText?: boolean;
  /** 中心文字标题 */
  centerTextTitle?: string;
  /** 中心文字副标题 */
  centerTextSubTitle?: string;
  /** 是否显示玫瑰图效果 */
  roseType?: 'radius' | 'area' | false;
  /** 自定义配置 */
  options?: EChartsOption;
}

/**
 * 饼图组件
 */
const PieChart: React.FC<PieChartProps> = ({
  data,
  showLegend = true,
  showLabel = true,
  showLabelLine = true,
  showCenterText = false,
  centerTextTitle = '总计',
  centerTextSubTitle = '',
  roseType = false,
  options = {},
  ...rest
}) => {
  // 计算总数
  const total = React.useMemo(() => {
    return data.reduce((sum, item) => sum + (item.value || 0), 0);
  }, [data]);

  // 构建系列数据
  const buildSeries = () => {
    if (!data || data.length === 0) return [];

    return [
      {
        name: rest.title || '数据',
        type: 'pie',
        radius: roseType ? [20, '70%'] : ['40%', '70%'],
        center: showCenterText ? ['50%', '50%'] : ['50%', '50%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 4,
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: {
          show: showLabel,
          formatter: (params: any) => {
            return `${params.name}: ${params.value} (${params.percent}%)`;
          },
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '14',
            fontWeight: 'bold',
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
        labelLine: {
          show: showLabelLine,
        },
        data: data.map((item) => ({
          name: item.name,
          value: item.value,
          itemStyle: {
            color: item.itemStyle?.color,
          },
        })),
        roseType: roseType || undefined,
      },
    ];
  };

  // 构建图例配置
  const buildLegend = () => {
    if (!showLegend) return {};

    return {
      legend: {
        orient: 'vertical',
        right: 10,
        top: 'center',
        textStyle: {
          color: '#666',
        },
        data: data.map((item) => item.name),
      },
    };
  };

  // 构建中心文字
  const buildCenterText = () => {
    if (!showCenterText) return {};

    return {
      graphic: [
        {
          type: 'text',
          left: 'center',
          top: 'center',
          style: {
            text: centerTextTitle,
            textAlign: 'center',
            fill: '#333',
            fontSize: 14,
            fontWeight: 'bold',
          },
        },
        {
          type: 'text',
          left: 'center',
          top: '60%',
          style: {
            text: total.toString(),
            textAlign: 'center',
            fill: '#1890ff',
            fontSize: 24,
            fontWeight: 'bold',
          },
        },
        centerTextSubTitle
          ? {
              type: 'text',
              left: 'center',
              top: '75%',
              style: {
                text: centerTextSubTitle,
                textAlign: 'center',
                fill: '#999',
                fontSize: 12,
              },
            }
          : undefined,
      ].filter(Boolean),
    };
  };

  // 合并配置
  const chartOptions: EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        return `${params.marker} ${params.name}<br/>
                数值: ${params.value}<br/>
                占比: ${params.percent}%`;
      },
    },
    ...buildLegend(),
    ...buildCenterText(),
    series: buildSeries() as any,
    ...options,
  };

  return <BaseChart type="pie" data={data} options={chartOptions} {...rest} />;
};

export default PieChart;
