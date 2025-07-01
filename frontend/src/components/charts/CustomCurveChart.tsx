import React, { useState } from 'react';
import {
  Card,
  Select,
  Button,
  Space,
  Row,
  Col,
  Form,
  ColorPicker,
  InputNumber,
  Switch,
  Divider,
  message,
  // Tooltip,
  Tag,
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  LineChartOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import BaseChart from './BaseChart';
import type { EChartsOption } from 'echarts';
// import type { ChartData } from '@/types/chart';

const { Option } = Select;

/**
 * 曲线配置接口
 */
interface CurveConfig {
  id: string;
  name: string;
  xColumn: string;
  yColumn: string;
  groupColumn?: string; // 状态量/分组列
  color: string;
  lineType: 'solid' | 'dashed' | 'dotted';
  lineWidth: number;
  showSymbol: boolean;
  symbolSize: number;
  smooth: boolean;
  visible: boolean;
}

/**
 * 数据集接口
 */
interface Dataset {
  id: string;
  name: string;
  columns: string[];
  data: Record<string, any>[];
}

interface CustomCurveChartProps {
  datasets: Dataset[];
  onDataRequest?: (datasetId: string) => Promise<Record<string, any>[]>;
  style?: React.CSSProperties;
  className?: string;
}

/**
 * 自定义曲线图组件
 * 类似Origin软件的曲线图绘制功能
 */
const CustomCurveChart: React.FC<CustomCurveChartProps> = ({
  datasets = [],
  onDataRequest,
  style,
  className,
}) => {
  const [curves, setCurves] = useState<CurveConfig[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<string>('');
  const [chartData, setChartData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  // 获取当前数据集
  const currentDataset = datasets.find(d => d.id === selectedDataset);
  const availableColumns = currentDataset?.columns || [];

  /**
   * 添加新曲线
   */
  const addCurve = () => {
    if (!selectedDataset) {
      message.warning('请先选择数据集');
      return;
    }

    const newCurve: CurveConfig = {
      id: `curve_${Date.now()}`,
      name: `曲线 ${curves.length + 1}`,
      xColumn: '',
      yColumn: '',
      groupColumn: undefined,
      color: `hsl(${(curves.length * 137.5) % 360}, 70%, 50%)`,
      lineType: 'solid',
      lineWidth: 2,
      showSymbol: true,
      symbolSize: 6,
      smooth: false,
      visible: true,
    };

    setCurves([...curves, newCurve]);
  };

  /**
   * 删除曲线
   */
  const removeCurve = (curveId: string) => {
    setCurves(curves.filter(c => c.id !== curveId));
  };

  /**
   * 更新曲线配置
   */
  const updateCurve = (curveId: string, updates: Partial<CurveConfig>) => {
    setCurves(curves.map(c =>
      c.id === curveId ? { ...c, ...updates } : c
    ));
  };

  /**
   * 生成图表数据
   */
  const generateChartData = async () => {
    if (!currentDataset || curves.length === 0) {
      message.warning('请添加至少一条曲线');
      return;
    }

    setLoading(true);
    try {
      let data = currentDataset.data;

      // 如果有数据请求回调，使用它获取最新数据
      if (onDataRequest) {
        data = await onDataRequest(selectedDataset);
      }

      const series: any[] = [];
      const xAxisData = new Set<string>();

      // 为每条曲线生成数据
      for (const curve of curves) {
        if (!curve.visible || !curve.xColumn || !curve.yColumn) continue;

        if (curve.groupColumn) {
          // 按分组列分组
          const groups = new Map<string, any[]>();
          data.forEach(row => {
            const groupValue = String(row[curve.groupColumn!]);
            if (!groups.has(groupValue)) {
              groups.set(groupValue, []);
            }
            groups.get(groupValue)!.push(row);
          });

          // 为每个分组创建一个系列
          groups.forEach((groupData, groupName) => {
            const seriesData = groupData
              .filter(row => row[curve.xColumn] != null && row[curve.yColumn] != null)
              .map(row => [row[curve.xColumn], row[curve.yColumn]])
              .sort((a, b) => a[0] - b[0]); // 按X轴排序

            seriesData.forEach(([x]) => xAxisData.add(String(x)));

            series.push({
              name: `${curve.name} - ${groupName}`,
              type: 'line',
              data: seriesData,
              lineStyle: {
                color: curve.color,
                type: curve.lineType,
                width: curve.lineWidth,
              },
              itemStyle: {
                color: curve.color,
              },
              symbol: curve.showSymbol ? 'circle' : 'none',
              symbolSize: curve.symbolSize,
              smooth: curve.smooth,
            });
          });
        } else {
          // 单一曲线
          const seriesData = data
            .filter(row => row[curve.xColumn] != null && row[curve.yColumn] != null)
            .map(row => [row[curve.xColumn], row[curve.yColumn]])
            .sort((a, b) => a[0] - b[0]); // 按X轴排序

          seriesData.forEach(([x]) => xAxisData.add(String(x)));

          series.push({
            name: curve.name,
            type: 'line',
            data: seriesData,
            lineStyle: {
              color: curve.color,
              type: curve.lineType,
              width: curve.lineWidth,
            },
            itemStyle: {
              color: curve.color,
            },
            symbol: curve.showSymbol ? 'circle' : 'none',
            symbolSize: curve.symbolSize,
            smooth: curve.smooth,
          });
        }
      }

      setChartData(series);
      message.success('图表生成成功');
    } catch (error) {
      console.error('生成图表数据失败:', error);
      message.error('生成图表数据失败');
    } finally {
      setLoading(false);
    }
  };

  /**
   * 渲染曲线配置项
   */
  const renderCurveConfig = (curve: CurveConfig, index: number) => (
    <Card
      key={curve.id}
      size="small"
      title={
        <Space>
          <LineChartOutlined style={{ color: curve.color }} />
          <span>{curve.name}</span>
          <Switch
            size="small"
            checked={curve.visible}
            onChange={(visible) => updateCurve(curve.id, { visible })}
          />
        </Space>
      }
      extra={
        <Button
          type="text"
          danger
          size="small"
          icon={<DeleteOutlined />}
          onClick={() => removeCurve(curve.id)}
        />
      }
      style={{ marginBottom: 16 }}
    >
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Form.Item label="曲线名称" style={{ marginBottom: 8 }}>
            <input
              type="text"
              value={curve.name}
              onChange={(e) => updateCurve(curve.id, { name: e.target.value })}
              style={{ width: '100%', padding: '4px 8px', border: '1px solid #d9d9d9', borderRadius: '4px' }}
            />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item label="颜色" style={{ marginBottom: 8 }}>
            <ColorPicker
              value={curve.color}
              onChange={(color) => updateCurve(curve.id, { color: color.toHexString() })}
            />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item label="X轴数据" style={{ marginBottom: 8 }}>
            <Select
              value={curve.xColumn}
              onChange={(value) => updateCurve(curve.id, { xColumn: value })}
              placeholder="选择X轴列"
              style={{ width: '100%' }}
            >
              {availableColumns.map(col => (
                <Option key={col} value={col}>{col}</Option>
              ))}
            </Select>
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item label="Y轴数据" style={{ marginBottom: 8 }}>
            <Select
              value={curve.yColumn}
              onChange={(value) => updateCurve(curve.id, { yColumn: value })}
              placeholder="选择Y轴列"
              style={{ width: '100%' }}
            >
              {availableColumns.map(col => (
                <Option key={col} value={col}>{col}</Option>
              ))}
            </Select>
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item label="分组列(可选)" style={{ marginBottom: 8 }}>
            <Select
              value={curve.groupColumn}
              onChange={(value) => updateCurve(curve.id, { groupColumn: value })}
              placeholder="选择分组列"
              allowClear
              style={{ width: '100%' }}
            >
              {availableColumns.map(col => (
                <Option key={col} value={col}>{col}</Option>
              ))}
            </Select>
          </Form.Item>
        </Col>

        {showSettings && (
          <>
            <Col span={8}>
              <Form.Item label="线型" style={{ marginBottom: 8 }}>
                <Select
                  value={curve.lineType}
                  onChange={(value) => updateCurve(curve.id, { lineType: value })}
                >
                  <Option value="solid">实线</Option>
                  <Option value="dashed">虚线</Option>
                  <Option value="dotted">点线</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item label="线宽" style={{ marginBottom: 8 }}>
                <InputNumber
                  min={1}
                  max={10}
                  value={curve.lineWidth}
                  onChange={(value) => updateCurve(curve.id, { lineWidth: value || 2 })}
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item label="符号大小" style={{ marginBottom: 8 }}>
                <InputNumber
                  min={2}
                  max={20}
                  value={curve.symbolSize}
                  onChange={(value) => updateCurve(curve.id, { symbolSize: value || 6 })}
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
            <Col span={24}>
              <Space>
                <span>显示符号:</span>
                <Switch
                  size="small"
                  checked={curve.showSymbol}
                  onChange={(checked) => updateCurve(curve.id, { showSymbol: checked })}
                />
                <span>平滑曲线:</span>
                <Switch
                  size="small"
                  checked={curve.smooth}
                  onChange={(checked) => updateCurve(curve.id, { smooth: checked })}
                />
              </Space>
            </Col>
          </>
        )}
      </Row>
    </Card>
  );

  // 生成ECharts配置
  const chartOptions: EChartsOption = {
    title: {
      text: '自定义曲线图',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
      },
    },
    legend: {
      top: 30,
      type: 'scroll',
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'value',
      name: curves.find(c => c.visible && c.xColumn)?.xColumn || 'X轴',
      nameLocation: 'middle',
      nameGap: 30,
    },
    yAxis: {
      type: 'value',
      name: curves.find(c => c.visible && c.yColumn)?.yColumn || 'Y轴',
      nameLocation: 'middle',
      nameGap: 50,
    },
    series: chartData,
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: 0,
      },
      {
        type: 'inside',
        yAxisIndex: 0,
      },
      {
        type: 'slider',
        xAxisIndex: 0,
        bottom: 10,
      },
    ],
  };

  return (
    <div style={style} className={className}>
      <Card title="自定义曲线图" style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          {/* 数据集选择 */}
          <Row gutter={16}>
            <Col span={12}>
              <Select
                placeholder="选择数据集"
                style={{ width: '100%' }}
                value={selectedDataset}
                onChange={(value) => {
                  setSelectedDataset(value);
                  setCurves([]); // 清空曲线配置
                  setChartData([]);
                }}
              >
                {datasets.map(dataset => (
                  <Option key={dataset.id} value={dataset.id}>
                    {dataset.name}
                  </Option>
                ))}
              </Select>
            </Col>
            <Col span={12}>
              <Space>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={addCurve}
                  disabled={!selectedDataset}
                >
                  添加曲线
                </Button>
                <Button
                  icon={<SettingOutlined />}
                  onClick={() => setShowSettings(!showSettings)}
                >
                  {showSettings ? '隐藏' : '显示'}高级设置
                </Button>
                <Button
                  type="primary"
                  onClick={generateChartData}
                  loading={loading}
                  disabled={curves.length === 0}
                >
                  生成图表
                </Button>
              </Space>
            </Col>
          </Row>

          {/* 当前数据集信息 */}
          {currentDataset && (
            <div>
              <Tag color="blue">数据集: {currentDataset.name}</Tag>
              <Tag color="green">列数: {currentDataset.columns.length}</Tag>
              <Tag color="orange">行数: {currentDataset.data.length}</Tag>
            </div>
          )}

          <Divider />

          {/* 曲线配置 */}
          {curves.map((curve, index) => renderCurveConfig(curve, index))}

          {curves.length === 0 && selectedDataset && (
            <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
              <LineChartOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
              <p>暂无曲线配置，点击"添加曲线"开始创建</p>
            </div>
          )}
        </Space>
      </Card>

      {/* 图表显示 */}
      {chartData.length > 0 && (
        <Card title="图表预览">
          <BaseChart
            options={chartOptions}
            height="500px"
            loading={loading}
          />
        </Card>
      )}
    </div>
  );
};

export default CustomCurveChart;
