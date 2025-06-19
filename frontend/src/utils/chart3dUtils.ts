import * as THREE from 'three';
import { Vector3, Color, BufferGeometry, Float32BufferAttribute } from 'three';

// 生成3D散点数据
export const generateScatterData = (count: number, seriesCount: number = 3) => {
  const series = [];
  const colors = [
    '#FF5252', '#FF4081', '#E040FB', '#7C4DFF',
    '#536DFE', '#448AFF', '#40C4FF', '#18FFFF',
    '#64FFDA', '#69F0AE', '#B2FF59', '#EEFF41',
    '#FFFF00', '#FFD740', '#FFAB40', '#FF6E40'
  ];

  for (let s = 0; s < seriesCount; s++) {
    const seriesColor = colors[s % colors.length];
    const seriesName = `系列 ${s + 1}`;
    const seriesId = `series-${s}`;
    
    for (let i = 0; i < count; i++) {
      const x = (Math.random() - 0.5) * 10;
      const y = (Math.random() - 0.5) * 10;
      const z = Math.sin(Math.sqrt(x * x + y * y)) + (Math.random() - 0.5) * 2;
      
      series.push({
        x,
        y,
        z,
        value: Math.abs(z) * 10,
        name: seriesName,
        series: seriesId,
        color: seriesColor,
      });
    }
  }
  
  return series;
};

// 计算3D边界框
export const computeBoundingBox = (points: { x: number; y: number; z: number }[]) => {
  if (points.length === 0) {
    return {
      min: new Vector3(0, 0, 0),
      max: new Vector3(0, 0, 0),
      center: new Vector3(0, 0, 0),
      size: new Vector3(0, 0, 0)
    };
  }

  const min = new Vector3(Infinity, Infinity, Infinity);
  const max = new Vector3(-Infinity, -Infinity, -Infinity);

  points.forEach(point => {
    min.x = Math.min(min.x, point.x);
    min.y = Math.min(min.y, point.y);
    min.z = Math.min(min.z, point.z);
    max.x = Math.max(max.x, point.x);
    max.y = Math.max(max.y, point.y);
    max.z = Math.max(max.z, point.z);
  });

  // 确保边界框不为零
  const epsilon = 0.001;
  if (min.x === max.x) { min.x -= epsilon; max.x += epsilon; }
  if (min.y === max.y) { min.y -= epsilon; max.y += epsilon; }
  if (min.z === max.z) { min.z -= epsilon; max.z += epsilon; }

  const center = new Vector3();
  center.addVectors(min, max).multiplyScalar(0.5);
  
  const size = new Vector3();
  size.subVectors(max, min);

  return { min, max, center, size };
};

// 创建点云几何体
export const createPointCloudGeometry = (points: { x: number; y: number; z: number }[]) => {
  const geometry = new BufferGeometry();
  const positions = new Float32Array(points.length * 3);
  
  points.forEach((point, i) => {
    positions[i * 3] = point.x;
    positions[i * 3 + 1] = point.y;
    positions[i * 3 + 2] = point.z;
  });
  
  geometry.setAttribute('position', new Float32BufferAttribute(positions, 3));
  return geometry;
};

// 创建颜色属性
export const createColorAttribute = (points: { color?: string | number | THREE.Color }[]) => {
  const colors = new Float32Array(points.length * 3);
  const color = new Color();
  
  points.forEach((point, i) => {
    if (point.color) {
      if (typeof point.color === 'string') {
        color.setStyle(point.color);
      } else if (typeof point.color === 'number') {
        color.setHex(point.color);
      } else {
        color.copy(point.color);
      }
    } else {
      // 默认颜色
      color.setHSL(i / points.length, 0.8, 0.6);
    }
    
    colors[i * 3] = color.r;
    colors[i * 3 + 1] = color.g;
    colors[i * 3 + 2] = color.b;
  });
  
  return colors;
};

// 创建大小属性
export const createSizeAttribute = (points: { value?: number }[], baseSize: number = 0.2, scale: number = 1) => {
  const sizes = new Float32Array(points.length);
  
  if (points.some(p => p.value !== undefined)) {
    // 如果有值，则根据值计算大小
    const values = points.map(p => p.value ?? 1);
    const minVal = Math.min(...values);
    const maxVal = Math.max(...values);
    const range = Math.max(0.1, maxVal - minVal);
    
    points.forEach((point, i) => {
      const value = point.value ?? 1;
      const normalized = (value - minVal) / range;
      sizes[i] = baseSize * (0.5 + normalized * 1.5) * scale;
    });
  } else {
    // 否则使用相同的大小
    sizes.fill(baseSize * scale);
  }
  
  return sizes;
};

// 创建坐标轴辅助对象
export const createAxesHelper = (size: number = 10) => {
  const axesHelper = new THREE.AxesHelper(size);
  
  // 设置坐标轴颜色
  const axesMaterial = axesHelper.material as THREE.Material[];
  axesMaterial[0].color = new THREE.Color(0xff0000); // X轴 - 红色
  axesMaterial[1].color = new THREE.Color(0x00ff00); // Y轴 - 绿色
  axesMaterial[2].color = new THREE.Color(0x0000ff); // Z轴 - 蓝色
  
  return axesHelper;
};

// 创建网格辅助对象
export const createGridHelper = (size: number = 10, divisions: number = 10) => {
  const gridHelper = new THREE.GridHelper(size, divisions, 0x888888, 0x444444);
  
  // 设置网格颜色
  const material = gridHelper.material as THREE.Material;
  material.opacity = 0.5;
  material.transparent = true;
  
  return gridHelper;
};

// 创建标签精灵
export const createLabelSprite = (text: string, color: string = '#ffffff', backgroundColor: string = 'rgba(0, 0, 0, 0.7)') => {
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  
  if (!context) {
    throw new Error('Could not get 2D context');
  }
  
  const fontSize = 14;
  const padding = 6;
  const borderRadius = 4;
  
  // 设置字体
  context.font = `bold ${fontSize}px Arial, sans-serif`;
  
  // 测量文本宽度
  const textWidth = context.measureText(text).width;
  
  // 设置画布大小
  canvas.width = Math.ceil(textWidth + padding * 2);
  canvas.height = Math.ceil(fontSize + padding * 2);
  
  // 重新设置字体（因为画布大小可能已更改）
  context.font = `bold ${fontSize}px Arial, sans-serif`;
  context.textBaseline = 'middle';
  context.textAlign = 'center';
  
  // 绘制圆角矩形背景
  context.fillStyle = backgroundColor;
  roundRect(context, 0, 0, canvas.width, canvas.height, borderRadius).fill();
  
  // 绘制文本
  context.fillStyle = color;
  context.fillText(text, canvas.width / 2, canvas.height / 2);
  
  // 创建纹理
  const texture = new THREE.CanvasTexture(canvas);
  
  // 创建精灵材质
  const spriteMaterial = new THREE.SpriteMaterial({
    map: texture,
    transparent: true,
    depthTest: false,
  });
  
  // 创建精灵
  const sprite = new THREE.Sprite(spriteMaterial);
  
  // 设置精灵大小（根据像素大小和缩放因子）
  const scale = 0.1; // 调整此值以更改标签大小
  sprite.scale.set(canvas.width * scale, canvas.height * scale, 1);
  
  return sprite;
};

// 辅助函数：绘制圆角矩形
const roundRect = (
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  width: number,
  height: number,
  radius: number
) => {
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + width - radius, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
  ctx.lineTo(x + width, y + height - radius);
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
  ctx.lineTo(x + radius, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
  ctx.lineTo(x, y + radius);
  ctx.quadraticCurveTo(x, y, x + radius, y);
  ctx.closePath();
  return ctx;
};

// 计算相机位置
export const calculateCameraPosition = (boundingBox: {
  min: THREE.Vector3;
  max: THREE.Vector3;
  center: THREE.Vector3;
  size: THREE.Vector3;
}, fov: number = 50, aspect: number = 1) => {
  const { center, size } = boundingBox;
  
  // 计算相机距离，确保整个场景在视图中
  const maxDim = Math.max(size.x, size.y, size.z);
  const cameraDistance = maxDim / (2 * Math.tan((fov * Math.PI / 180) / 2));
  
  // 计算相机位置（从场景中心偏移）
  const cameraPosition = new Vector3(
    center.x,
    center.y,
    center.z + cameraDistance * 1.5 // 向后移动一些
  );
  
  return {
    position: cameraPosition,
    lookAt: center,
    far: cameraDistance * 10 // 远平面距离
  };
};
