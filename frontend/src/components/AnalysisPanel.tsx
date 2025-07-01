import React, { useState, useEffect } from 'react';
import {
  Card,
  Tabs,
  Table,
  Select,
  Button,
  Space,
  Statistic,
  Row,
  Col,
  // Spin,
  Alert,
  message,
  InputNumber,
  // Checkbox,
} from 'antd';
import {
  BarChartOutlined,
  LineChartOutlined,
  DotChartOutlined,
  // FunctionOutlined,
  ClusterOutlined,
  FunctionOutlined,
} from '@ant-design/icons';

import CustomCurveChart from './charts/CustomCurveChart';

import { analysisService } from '../services/analysisService';
import type { DescriptiveStats,
  CorrelationMatrix,
  RegressionResult,
  ClusteringResult
} from '../services/analysisService';

import { useDataManager } from '../hooks/useDataManager';
// import BarChart from './charts/BarChart';
// import LineChart from './charts/LineChart';

const { TabPane } = Tabs;
const { Option } = Select;

interface AnalysisPanelProps {
  datasetId?: string;
}

/**
 * 数据分析面板组件
 * 提供描述性统计、相关性分析、回归分析、聚类分析等功能
 */
const AnalysisPanel: React.FC<AnalysisPanelProps> = ({ datasetId }) => {
  const { dataList } = useDataManager();
  const [selectedDataset, setSelectedDataset] = useState<string>(datasetId || '');
  const [loading, setLoading] = useState(false);

  // 描述性统计
  const [descriptiveStats, setDescriptiveStats] = useState<DescriptiveStats[]>([]);

  // 相关性分析
  const [correlationMatrix, setCorrelationMatrix] = useState<CorrelationMatrix | null>(null);

  // 回归分析
  const [regressionResult, setRegressionResult] = useState<RegressionResult | null>(null);
  const [targetColumn, setTargetColumn] = useState<string>('');
  const [featureColumns, setFeatureColumns] = useState<string[]>([]);

  // 聚类分析
  const [clusteringResult, setClusteringResult] = useState<ClusteringResult | null>(null);
  const [clusterColumns, setClusterColumns] = useState<string[]>([]);
  const [nClusters, setNClusters] = useState<number>(3);

  // 获取当前数据集信息
  const currentDataset = dataList.find(d => d.id === selectedDataset);
  const availableColumns = currentDataset?.columns || [];

  // 获取描述性统计
  const fetchDescriptiveStats = async () => {
    if (!selectedDataset) return;

    setLoading(true);
    try {
      const stats = await analysisService.getDescriptiveStats(selectedDataset);
      setDescriptiveStats(stats);
    } catch (error) {
      message.error('获取描述性统计失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取相关性矩阵
  const fetchCorrelationMatrix = async () => {
    if (!selectedDataset) return;

    setLoading(true);
    try {
      const matrix = await analysisService.getCorrelationMatrix(selectedDataset);
      setCorrelationMatrix(matrix);
    } catch (error) {
      message.error('获取相关性矩阵失败');
    } finally {
      setLoading(false);
    }
  };

  // 执行回归分析
  const performRegression = async () => {
    if (!selectedDataset || !targetColumn || featureColumns.length === 0) {
      message.warning('请选择目标列和特征列');
      return;
    }

    setLoading(true);
    try {
      const result = await analysisService.performRegression(
        selectedDataset,
        targetColumn,
        featureColumns
      );
      setRegressionResult(result);
      message.success('回归分析完成');
    } catch (error) {
      message.error('回归分析失败');
    } finally {
      setLoading(false);
    }
  };

  // 执行聚类分析
  const performClustering = async () => {
    if (!selectedDataset || clusterColumns.length === 0) {
      message.warning('请选择聚类列');
      return;
    }

    setLoading(true);
    try {
      const result = await analysisService.performClustering(
        selectedDataset,
        clusterColumns,
        nClusters
      );
      setClusteringResult(result);
      message.success('聚类分析完成');
    } catch (error) {
      message.error('聚类分析失败');
    } finally {
      setLoading(false);
    }
  };

  // 当数据集改变时重置状态
  useEffect(() => {
    setDescriptiveStats([]);
    setCorrelationMatrix(null);
    setRegressionResult(null);
    setClusteringResult(null);
    setTargetColumn('');
    setFeatureColumns([]);
    setClusterColumns([]);
  }, [selectedDataset]);

  // 描述性统计表格列
  const descriptiveColumns = [
    { title: '列名', dataIndex: 'column', key: 'column' },
    { title: '计数', dataIndex: 'count', key: 'count' },
    { title: '均值', dataIndex: 'mean', key: 'mean', render: (val: number) => val?.toFixed(2) },
    { title: '标准差', dataIndex: 'std', key: 'std', render: (val: number) => val?.toFixed(2) },
    { title: '最小值', dataIndex: 'min', key: 'min' },
    { title: '25%分位', dataIndex: 'q25', key: 'q25' },
    { title: '中位数', dataIndex: 'q50', key: 'q50' },
    { title: '75%分位', dataIndex: 'q75', key: 'q75' },
    { title: '最大值', dataIndex: 'max', key: 'max' },
  ];

  // 相关性矩阵表格列
  const correlationColumns = correlationMatrix?.columns.map(col => ({
    title: col,
    dataIndex: col,
    key: col,
    render: (val: number) => (
      <span style={{
        color: val > 0.7 ? '#52c41a' : val < -0.7 ? '#ff4d4f' : '#1890ff',
        fontWeight: Math.abs(val) > 0.7 ? 'bold' : 'normal'
      }}>
        {val?.toFixed(3)}
      </span>
    ),
  })) || [];

  // 相关性矩阵数据
  const correlationData = correlationMatrix?.matrix.map((row, index) => {
    const rowData: any = { key: index };
    correlationMatrix.columns.forEach((col, colIndex) => {
      rowData[col] = row[colIndex];
    });
    return rowData;
  }) || [];

  return (
    <Card title="数据分析" style={{ margin: '16px' }}>
      <Space direction="vertical" style={{ width: '100%' }}>
        {/* 数据集选择 */}
        <Select
          placeholder="选择数据集"
          style={{ width: 300 }}
          value={selectedDataset}
          onChange={setSelectedDataset}
        >
          {dataList.map(dataset => (
            <Option key={dataset.id} value={dataset.id}>
              {dataset.filename}
            </Option>
          ))}
        </Select>

        {selectedDataset && (
          <Tabs defaultActiveKey="descriptive">
            {/* 自定义曲线图 */}
            <TabPane
              tab={
                <span>
                  <FunctionOutlined />
                  自定义曲线图
                </span>
              }
              key="custom-curve"
            >
              <CustomCurveChart
                datasets={[
                  {
                    id: selectedDataset,
                    name: currentDataset?.filename || '当前数据集',
                    columns: availableColumns,
                    data: currentDataset?.data || [],
                  },
                ]}
                style={{ marginTop: 16 }}
              />
            </TabPane>
            {/* 描述性统计 */}
            <TabPane
              tab={
                <span>
                  <BarChartOutlined />
                  描述性统计
                </span>
              }
              key="descriptive"
            >
              <Space direction="vertical" style={{ width: '100%' }}>
                <Button
                  type="primary"
                  onClick={fetchDescriptiveStats}
                  loading={loading}
                >
                  生成描述性统计
                </Button>

                {descriptiveStats.length > 0 && (
                  <Table
                    dataSource={descriptiveStats.map((item, index) => ({ ...item, key: index }))}
                    columns={descriptiveColumns}
                    pagination={false}
                    size="small"
                  />
                )}
              </Space>
            </TabPane>

            {/* 相关性分析 */}
            <TabPane
              tab={
                <span>
                  <DotChartOutlined />
                  相关性分析
                </span>
              }
              key="correlation"
            >
              <Space direction="vertical" style={{ width: '100%' }}>
                <Button
                  type="primary"
                  onClick={fetchCorrelationMatrix}
                  loading={loading}
                >
                  生成相关性矩阵
                </Button>

                {correlationMatrix && (
                  <>
                    <Alert
                      message="相关性解读"
                      description="绿色表示强正相关(>0.7)，红色表示强负相关(<-0.7)，蓝色表示弱相关"
                      type="info"
                      showIcon
                    />
                    <Table
                      dataSource={correlationData}
                      columns={correlationColumns}
                      pagination={false}
                      size="small"
                      scroll={{ x: true }}
                    />
                  </>
                )}
              </Space>
            </TabPane>

            {/* 回归分析 */}
            <TabPane
              tab={
                <span>
                  <LineChartOutlined />
                  回归分析
                </span>
              }
              key="regression"
            >
              <Space direction="vertical" style={{ width: '100%' }}>
                <Row gutter={16}>
                  <Col span={8}>
                    <label>目标列：</label>
                    <Select
                      placeholder="选择目标列"
                      style={{ width: '100%' }}
                      value={targetColumn}
                      onChange={setTargetColumn}
                    >
                      {availableColumns.map(col => (
                        <Option key={col} value={col}>{col}</Option>
                      ))}
                    </Select>
                  </Col>
                  <Col span={16}>
                    <label>特征列：</label>
                    <Select
                      mode="multiple"
                      placeholder="选择特征列"
                      style={{ width: '100%' }}
                      value={featureColumns}
                      onChange={setFeatureColumns}
                    >
                      {availableColumns.filter(col => col !== targetColumn).map(col => (
                        <Option key={col} value={col}>{col}</Option>
                      ))}
                    </Select>
                  </Col>
                </Row>

                <Button
                  type="primary"
                  onClick={performRegression}
                  loading={loading}
                  disabled={!targetColumn || featureColumns.length === 0}
                >
                  执行回归分析
                </Button>

                {regressionResult && (
                  <Row gutter={16}>
                    <Col span={12}>
                      <Card title="回归系数" size="small">
                        {Object.entries(regressionResult.coefficients).map(([key, value]) => (
                          <Statistic
                            key={key}
                            title={key}
                            value={value}
                            precision={4}
                          />
                        ))}
                      </Card>
                    </Col>
                    <Col span={12}>
                      <Card title="模型评估" size="small">
                        <Statistic
                          title="R²决定系数"
                          value={regressionResult.rSquared}
                          precision={4}
                        />
                      </Card>
                    </Col>
                  </Row>
                )}
              </Space>
            </TabPane>

            {/* 聚类分析 */}
            <TabPane
              tab={
                <span>
                  <ClusterOutlined />
                  聚类分析
                </span>
              }
              key="clustering"
            >
              <Space direction="vertical" style={{ width: '100%' }}>
                <Row gutter={16}>
                  <Col span={12}>
                    <label>聚类列：</label>
                    <Select
                      mode="multiple"
                      placeholder="选择聚类列"
                      style={{ width: '100%' }}
                      value={clusterColumns}
                      onChange={setClusterColumns}
                    >
                      {availableColumns.map(col => (
                        <Option key={col} value={col}>{col}</Option>
                      ))}
                    </Select>
                  </Col>
                  <Col span={12}>
                    <label>聚类数量：</label>
                    <InputNumber
                      min={2}
                      max={10}
                      value={nClusters}
                      onChange={(value) => setNClusters(value || 3)}
                      style={{ width: '100%' }}
                    />
                  </Col>
                </Row>

                <Button
                  type="primary"
                  onClick={performClustering}
                  loading={loading}
                  disabled={clusterColumns.length === 0}
                >
                  执行聚类分析
                </Button>

                {clusteringResult && (
                  <Row gutter={16}>
                    <Col span={8}>
                      <Statistic
                        title="轮廓系数"
                        value={clusteringResult.silhouetteScore}
                        precision={4}
                        suffix="(越接近1越好)"
                      />
                    </Col>
                    <Col span={8}>
                      <Statistic
                        title="惯性"
                        value={clusteringResult.inertia}
                        precision={2}
                        suffix="(越小越好)"
                      />
                    </Col>
                    <Col span={8}>
                      <Statistic
                        title="聚类数量"
                        value={nClusters}
                      />
                    </Col>
                  </Row>
                )}
              </Space>
            </TabPane>
          </Tabs>
        )}
      </Space>
    </Card>
  );
};

export default AnalysisPanel;
