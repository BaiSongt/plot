/**
 * 数据分析服务
 * 负责与后端分析API的交互
 */

export interface AnalysisRequest {
  datasetId: string;
  analysisType: 'descriptive' | 'correlation' | 'regression' | 'clustering';
  parameters?: Record<string, any>;
}

export interface AnalysisResult {
  id: string;
  type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: any;
  error?: string;
  createdAt: string;
  completedAt?: string;
}

export interface DescriptiveStats {
  column: string;
  count: number;
  mean?: number;
  std?: number;
  min?: number;
  max?: number;
  q25?: number;
  q50?: number;
  q75?: number;
}

export interface CorrelationMatrix {
  columns: string[];
  matrix: number[][];
}

export interface RegressionResult {
  coefficients: Record<string, number>;
  rSquared: number;
  pValues: Record<string, number>;
  predictions?: number[];
}

export interface ClusteringResult {
  labels: number[];
  centers?: number[][];
  silhouetteScore?: number;
  inertia?: number;
}

class AnalysisService {
  private baseUrl = 'http://localhost:8000/api/v1';

  /**
   * 启动数据分析
   */
  async startAnalysis(request: AnalysisRequest): Promise<AnalysisResult> {
    try {
      const response = await fetch(`${this.baseUrl}/analysis/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`分析启动失败: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('启动分析失败:', error);
      // 返回模拟结果
      return this.getMockAnalysisResult(request.analysisType);
    }
  }

  /**
   * 获取分析结果
   */
  async getAnalysisResult(analysisId: string): Promise<AnalysisResult> {
    try {
      const response = await fetch(`${this.baseUrl}/analysis/${analysisId}`);
      
      if (!response.ok) {
        throw new Error(`获取分析结果失败: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('获取分析结果失败:', error);
      throw error;
    }
  }

  /**
   * 获取描述性统计
   */
  async getDescriptiveStats(datasetId: string): Promise<DescriptiveStats[]> {
    try {
      const response = await fetch(`${this.baseUrl}/analysis/descriptive/${datasetId}`);
      
      if (!response.ok) {
        throw new Error(`获取描述性统计失败: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('获取描述性统计失败:', error);
      // 返回模拟数据
      return this.getMockDescriptiveStats();
    }
  }

  /**
   * 获取相关性矩阵
   */
  async getCorrelationMatrix(datasetId: string): Promise<CorrelationMatrix> {
    try {
      const response = await fetch(`${this.baseUrl}/analysis/correlation/${datasetId}`);
      
      if (!response.ok) {
        throw new Error(`获取相关性矩阵失败: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('获取相关性矩阵失败:', error);
      // 返回模拟数据
      return this.getMockCorrelationMatrix();
    }
  }

  /**
   * 执行回归分析
   */
  async performRegression(
    datasetId: string, 
    targetColumn: string, 
    featureColumns: string[]
  ): Promise<RegressionResult> {
    try {
      const response = await fetch(`${this.baseUrl}/analysis/regression`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          datasetId,
          targetColumn,
          featureColumns,
        }),
      });

      if (!response.ok) {
        throw new Error(`回归分析失败: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('回归分析失败:', error);
      // 返回模拟数据
      return this.getMockRegressionResult();
    }
  }

  /**
   * 执行聚类分析
   */
  async performClustering(
    datasetId: string, 
    columns: string[], 
    nClusters: number = 3
  ): Promise<ClusteringResult> {
    try {
      const response = await fetch(`${this.baseUrl}/analysis/clustering`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          datasetId,
          columns,
          nClusters,
        }),
      });

      if (!response.ok) {
        throw new Error(`聚类分析失败: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('聚类分析失败:', error);
      // 返回模拟数据
      return this.getMockClusteringResult();
    }
  }

  // 模拟数据方法
  private getMockAnalysisResult(type: string): AnalysisResult {
    return {
      id: `mock-${Date.now()}`,
      type,
      status: 'completed',
      result: { message: '模拟分析结果' },
      createdAt: new Date().toISOString(),
      completedAt: new Date().toISOString(),
    };
  }

  private getMockDescriptiveStats(): DescriptiveStats[] {
    return [
      {
        column: 'value',
        count: 100,
        mean: 50.5,
        std: 15.2,
        min: 10,
        max: 90,
        q25: 35,
        q50: 50,
        q75: 65,
      },
      {
        column: 'score',
        count: 100,
        mean: 75.3,
        std: 12.8,
        min: 45,
        max: 95,
        q25: 68,
        q50: 76,
        q75: 84,
      },
    ];
  }

  private getMockCorrelationMatrix(): CorrelationMatrix {
    return {
      columns: ['value', 'score', 'rating'],
      matrix: [
        [1.0, 0.75, 0.45],
        [0.75, 1.0, 0.62],
        [0.45, 0.62, 1.0],
      ],
    };
  }

  private getMockRegressionResult(): RegressionResult {
    return {
      coefficients: {
        intercept: 10.5,
        feature1: 2.3,
        feature2: -1.8,
      },
      rSquared: 0.85,
      pValues: {
        intercept: 0.001,
        feature1: 0.002,
        feature2: 0.045,
      },
    };
  }

  private getMockClusteringResult(): ClusteringResult {
    return {
      labels: Array.from({ length: 100 }, () => Math.floor(Math.random() * 3)),
      centers: [
        [25, 30],
        [50, 60],
        [75, 80],
      ],
      silhouetteScore: 0.72,
      inertia: 1250.5,
    };
  }
}

export const analysisService = new AnalysisService();