import React, { useEffect, useRef, useState } from 'react';
import * as echarts from 'echarts';
import type { SetOptionOpts } from 'echarts';
import type { EChartsType, EChartsOption } from 'echarts';
import type { ChartOptions, ChartData, ChartSize } from '../../types/chart';

interface BaseChartProps extends Omit<ChartOptions, 'theme' | 'onRendered'> {
  /** 图表数据 */
  data?: ChartData[];
  /** 图表配置 */
  options?: EChartsOption;
  /** 图表类型 */
  type?: string;
  /** 是否显示加载状态 */
  loading?: boolean;
  /** 加载状态文本 */
  loadingText?: string;
  /** 图表尺寸 */
  size?: ChartSize;
  /** 主题 */
  theme?: string | object;
  /** 是否自动调整大小 */
  autoResize?: boolean;
  /** 图表渲染完成回调 */
  onRendered?: (instance: EChartsType) => void;
}

/**
 * 基础图表组件
 * 所有图表组件的基类，封装了ECharts的通用逻辑
 */
const BaseChart: React.FC<BaseChartProps> = ({
  data = [],
  options = {},
  type = 'line',
  loading = false,
  loadingText = '加载中...',
  title,
  subtext,
  width = '100%',
  height = '400px',
  theme,
  autoResize = true,
  style = {},
  onRendered,
  onEvents,
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const [chart, setChart] = useState<EChartsType | null>(null);

  // 初始化图表
  useEffect(() => {
    if (!chartRef.current) return;

    // 初始化图表实例
    const chartInstance = echarts.init(chartRef.current, theme);
    setChart(chartInstance);

    // 组件卸载时销毁图表实例
    return () => {
      chartInstance.dispose();
      setChart(null);
    };
  }, [theme]);

  // 更新图表数据
  useEffect(() => {
    if (!chart) return;

    // 合并默认配置和自定义配置
    const defaultOptions: EChartsOption = {
      title: {
        text: title,
        subtext: subtext,
        left: 'center',
      },
      tooltip: {
        trigger: 'item',
        axisPointer: {
          type: 'shadow',
        },
      },
      legend: {
        data: data.map((item) => item.name),
        bottom: 0,
      },
      series: [
        {
          name: title || '数据',
          type: type as any,
          data: data.map((item) => ({
            name: item.name,
            value: item.value,
            itemStyle: item.itemStyle,
          })),
        },
      ],
    };

    // 合并配置
    const mergedOptions: EChartsOption = {
      ...defaultOptions,
      ...options,
    };

    // 设置图表配置
    chart.setOption(mergedOptions, {
      notMerge: true,
    } as SetOptionOpts);

    // 触发渲染完成回调
    if (onRendered) {
      onRendered(chart);
    }

    // 绑定事件
    if (onEvents) {
      Object.entries(onEvents).forEach(([eventName, handler]) => {
        chart.on(eventName, handler);
      });

      // 清理事件
      return () => {
        if (chart) {
          Object.entries(onEvents).forEach(([eventName, handler]) => {
            chart.off(eventName, handler);
          });
        }
      };
    }
  }, [chart, data, options, title, subtext, type, onRendered, onEvents]);

  // 处理加载状态
  useEffect(() => {
    if (!chart) return;

    if (loading) {
      chart.showLoading('default', {
        text: loadingText,
        color: '#1890ff',
        textColor: '#000',
        maskColor: 'rgba(255, 255, 255, 0.8)',
      });
    } else {
      chart.hideLoading();
    }
  }, [chart, loading, loadingText]);

  // 处理窗口大小变化
  useEffect(() => {
    if (!autoResize || !chart) return;

    const handleResize = () => {
      chart.resize();
    };

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [autoResize, chart]);

  return (
    <div
      ref={chartRef}
      style={{
        width,
        height,
        ...style,
      }}
    />
  );
};

export default BaseChart;
