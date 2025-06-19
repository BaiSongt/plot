import { useState, useEffect, useCallback } from 'react';

interface ChartDimensions {
  width: number;
  height: number;
  margin?: {
    top: number;
    right: number;
    bottom: number;
    left: number;
  };
}

export const useResponsiveChart = (
  containerRef: React.RefObject<HTMLDivElement>,
  aspectRatio: number = 16 / 9
): ChartDimensions => {
  const [dimensions, setDimensions] = useState<ChartDimensions>({
    width: 0,
    height: 0,
    margin: {
      top: 20,
      right: 20,
      bottom: 40,
      left: 60,
    },
  });

  const updateDimensions = useCallback(() => {
    if (!containerRef.current) return;

    const containerWidth = containerRef.current.clientWidth;
    const containerHeight = containerRef.current.clientHeight;
    
    // 计算保持宽高比的最大可能尺寸
    let width, height;
    const containerAspectRatio = containerWidth / containerHeight;
    
    if (containerAspectRatio > aspectRatio) {
      // 容器比图表宽
      height = containerHeight * 0.9; // 留出一些边距
      width = height * aspectRatio;
    } else {
      // 容器比图表高或比例相同
      width = containerWidth * 0.95; // 留出一些边距
      height = width / aspectRatio;
    }
    
    // 确保尺寸不会超过容器
    width = Math.min(width, containerWidth * 0.95);
    height = Math.min(height, containerHeight * 0.9);
    
    setDimensions(prev => ({
      ...prev,
      width: Math.max(100, width), // 确保最小宽度
      height: Math.max(100, height), // 确保最小高度
    }));
  }, [containerRef, aspectRatio]);

  useEffect(() => {
    updateDimensions();
    
    // 添加窗口大小变化监听
    window.addEventListener('resize', updateDimensions);
    
    // 添加 ResizeObserver 监听容器大小变化
    let resizeObserver: ResizeObserver | null = null;
    if (containerRef.current) {
      resizeObserver = new ResizeObserver(updateDimensions);
      resizeObserver.observe(containerRef.current);
    }
    
    return () => {
      window.removeEventListener('resize', updateDimensions);
      if (resizeObserver && containerRef.current) {
        resizeObserver.unobserve(containerRef.current);
      }
    };
  }, [updateDimensions, containerRef]);

  return dimensions;
};

// 辅助函数：根据数据范围计算合适的刻度
interface ScaleDomain {
  min: number;
  max: number;
  step: number;
  ticks: number[];
}

export const calculateNiceScale = (min: number, max: number, tickCount: number = 5): ScaleDomain => {
  if (min === max) {
    // 如果最小值和最大值相同，创建一个包含单个刻度的范围
    return {
      min: min - 1,
      max: max + 1,
      step: 1,
      ticks: [min]
    };
  }

  // 计算一个合适的步长
  const range = max - min;
  const rawStep = range / (tickCount - 1);
  const exponent = Math.floor(Math.log10(rawStep));
  const factor = Math.pow(10, exponent);
  const step = Math.ceil(rawStep / factor) * factor;

  // 计算最小值和最大值
  const niceMin = Math.floor(min / step) * step;
  const niceMax = Math.ceil(max / step) * step;
  
  // 生成刻度
  const ticks: number[] = [];
  for (let i = 0; i <= tickCount; i++) {
    ticks.push(niceMin + i * step);
  }

  return {
    min: niceMin,
    max: niceMax,
    step,
    ticks
  };
};

// 辅助函数：格式化数值
interface FormatNumberOptions {
  precision?: number;
  suffix?: string;
  prefix?: string;
  k?: boolean; // 是否使用千分位分隔符
}

export const formatNumber = (
  value: number, 
  options: FormatNumberOptions = {}
): string => {
  const { precision = 2, suffix = '', prefix = '', k = true } = options;
  
  // 处理非数字
  if (isNaN(value) || value === null || value === undefined) {
    return '--';
  }
  
  // 处理无穷大
  if (!isFinite(value)) {
    return value > 0 ? '∞' : '-∞';
  }
  
  // 处理小数精度
  let formattedValue: string;
  if (precision >= 0) {
    formattedValue = value.toFixed(precision);
  } else {
    formattedValue = value.toString();
  }
  
  // 添加千分位分隔符
  if (k) {
    const parts = formattedValue.split('.');
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    formattedValue = parts.join('.');
  }
  
  // 添加前缀和后缀
  return `${prefix}${formattedValue}${suffix}`;
};

// 辅助函数：生成渐变色
interface ColorStop {
  offset: number; // 0-1
  color: string;
}

export const createGradient = (
  ctx: CanvasRenderingContext2D,
  x0: number,
  y0: number,
  x1: number,
  y1: number,
  colorStops: ColorStop[]
): CanvasGradient => {
  const gradient = ctx.createLinearGradient(x0, y0, x1, y1);
  colorStops.forEach(stop => {
    gradient.addColorStop(stop.offset, stop.color);
  });
  return gradient;
};

// 辅助函数：深拷贝对象
export const deepClone = <T>(obj: T): T => {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }
  
  if (Array.isArray(obj)) {
    return obj.map(item => deepClone(item)) as unknown as T;
  }
  
  const result: any = {};
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      result[key] = deepClone(obj[key as keyof T]);
    }
  }
  
  return result as T;
};
