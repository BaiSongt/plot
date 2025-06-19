import React from 'react';
import BaseChart from './BaseChart';
import { EChartsOption } from 'echarts';
import { ChartData, ChartOptions } from '@/types/chart';

interface ScatterData extends ChartData {
  /** X轴值 */
  x: number;
  /** Y轴值 */
  y: number;
  /** 点的大小 */
  symbolSize?: number;
  /** 点的形状 */
  symbol?: string;
}

interface ScatterChartProps extends ChartOptions {
  /** 散点图数据 */
  data: ScatterData[];
  /** X轴名称 */
  xAxisName?: string;
  /** Y轴名称 */
  yAxisName?: string;
  /** 是否显示图例 */
  showLegend?: boolean;
  /** 是否显示数据标签 */
  showLabel?: boolean;
  /** 是否显示回归线 */
  showRegressionLine?: boolean;
  /** 点的最小大小 */
  minSymbolSize?: number;
  /** 点的最大大小 */
  maxSymbolSize?: number;
  /** 自定义配置 */
  options?: EChartsOption;
}

/**
 * 散点图组件
 */
const ScatterChart: React.FC<ScatterChartProps> = ({
  data,
  xAxisName,
  yAxisName,
  showLegend = true,
  showLabel = false,
  showRegressionLine = false,
  minSymbolSize = 10,
  maxSymbolSize = 40,
  options = {},
  ...rest
}) => {
  // 构建系列数据
  const buildSeries = () => {
    if (!data || data.length === 0) return [];

    const series: any[] = [
      {
        name: rest.title || '数据',
        type: 'scatter',
        symbolSize: (val: number[]) => {
          // 根据数据范围动态调整点的大小
          const sizes = data.map((item) => item.symbolSize || 10);
          const minSize = Math.min(...sizes);
          const maxSize = Math.max(...sizes);
          
          if (minSize === maxSize) return minSize;
          
          const sizeRange = maxSize - minSize;
          const normalizedSize = ((val[2] || minSize) - minSize) / sizeRange;
          return minSymbolSize + normalizedSize * (maxSymbolSize - minSymbolSize);
        },
        data: data.map((item) => ({
          name: item.name,
          value: [item.x, item.y, item.symbolSize || 10],
          itemStyle: {
            color: item.itemStyle?.color,
          },
        })),
        label: {
          show: showLabel,
          formatter: (params: any) => {
            return data[params.dataIndex]?.name || '';
          },
          position: 'top',
        },
        emphasis: {
          label: {
            show: true,
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ];

    // 添加回归线
    if (showRegressionLine && data.length > 1) {
      const xData = data.map((item) => item.x);
      const yData = data.map((item) => item.y);
      
      // 计算回归线
      const regression = calculateRegression(xData, yData);
      
      // 获取X轴范围
      const xMin = Math.min(...xData);
      const xMax = Math.max(...xData);
      
      // 计算回归线起点和终点
      const start = [xMin, regression.slope * xMin + regression.intercept];
      const end = [xMax, regression.slope * xMax + regression.intercept];
      
      // 添加回归线系列
      series.push({
        type: 'line',
        data: [start, end],
        symbol: 'none',
        lineStyle: {
          type: 'dashed',
          color: '#999',
        },
        tooltip: {
          show: false,
        },
        silent: true,
      });
      
      // 添加R²值
      if (regression.rSquared) {
        series[0].markLine = {
          silent: true,
          symbol: 'none',
          lineStyle: {
            color: '#999',
            type: 'dashed',
          },
          label: {
            formatter: `y = ${regression.slope.toFixed(2)}x + ${regression.intercept.toFixed(2)}\nR² = ${regression.rSquared.toFixed(4)}`,
            align: 'right',
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            padding: [2, 5],
            borderRadius: 4,
          },
          data: [
            [
              { coord: [xMin, regression.slope * xMin + regression.intercept] },
              { coord: [xMax, regression.slope * xMax + regression.intercept] },
            ],
          ],
        };
      }
    }

    return series;
  };

  // 计算线性回归
  const calculateRegression = (xData: number[], yData: number[]) => {
    const n = xData.length;
    let sumX = 0;
    let sumY = 0;
    let sumXY = 0;
    let sumX2 = 0;
    let sumY2 = 0;

    for (let i = 0; i < n; i++) {
      sumX += xData[i];
      sumY += yData[i];
      sumXY += xData[i] * yData[i];
      sumX2 += xData[i] * xData[i];
      sumY2 += yData[i] * yData[i];
    }


    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;
    
    // 计算R²
    let ssTot = 0;
    let ssRes = 0;
    const yMean = sumY / n;
    
    for (let i = 0; i < n; i++) {
      const yPred = slope * xData[i] + intercept;
      ssTot += Math.pow(yData[i] - yMean, 2);
      ssRes += Math.pow(yData[i] - yPred, 2);
    }
    
    const rSquared = 1 - (ssRes / ssTot);

    return { slope, intercept, rSquared };
  };

  // 构建X轴配置
  const buildXAxis = () => ({
    name: xAxisName,
    nameLocation: 'middle',
    nameGap: 30,
    nameTextStyle: {
      color: '#666',
      fontSize: 12,
    },
    type: 'value',
    scale: true,
    axisLine: {
      lineStyle: {
        color: '#d9d9d9',
      },
    },
    axisLabel: {
      color: '#666',
    },
    splitLine: {
      lineStyle: {
        type: 'dashed',
        color: '#f0f0f0',
      },
    },
  });

  // 构建Y轴配置
  const buildYAxis = () => ({
    name: yAxisName,
    nameLocation: 'middle',
    nameGap: 40,
    nameTextStyle: {
      color: '#666',
      fontSize: 12,
    },
    type: 'value',
    scale: true,
    axisLine: {
      lineStyle: {
        color: '#d9d9d9',
      },
    },
    axisLabel: {
      color: '#666',
    },
    splitLine: {
      lineStyle: {
        type: 'dashed',
        color: '#f0f0f0',
      },
    },
  });

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
        type: 'cross',
        label: {
          backgroundColor: '#6a7985',
        },
      },
      formatter: (params: any) => {
        const param = params[0];
        if (!param || !param.value) return '';
        
        const dataItem = data[param.dataIndex];
        let tooltip = `<div style="margin-bottom: 5px; font-weight: bold;">${dataItem?.name || '数据点'}</div>`;
        tooltip += `<div>${xAxisName || 'X'}: ${param.value[0]}</div>`;
        tooltip += `<div>${yAxisName || 'Y'}: ${param.value[1]}</div>`;
        
        if (dataItem?.symbolSize) {
          tooltip += `<div>大小: ${dataItem.symbolSize}</div>`;
        }
        
        return tooltip;
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

  return <BaseChart type="scatter" data={data} options={chartOptions} {...rest} />;
};

export default ScatterChart;
