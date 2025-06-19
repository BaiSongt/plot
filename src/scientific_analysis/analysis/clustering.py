"""聚类分析

提供聚类分析功能，包括K-means聚类、层次聚类、DBSCAN等。
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import pandas as pd
import numpy as np
from enum import Enum, auto
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

from .base import BaseAnalyzer, AnalysisResult
from scientific_analysis.models.dataset import Dataset
from scientific_analysis.visualization import ScatterChart, HeatmapChart


class ClusteringMethod(Enum):
    """聚类方法枚举"""
    KMEANS = auto()       # K-means聚类
    HIERARCHICAL = auto()  # 层次聚类
    DBSCAN = auto()        # 基于密度的聚类
    GAUSSIAN_MIXTURE = auto()  # 高斯混合模型


class ClusteringAnalyzer(BaseAnalyzer):
    """聚类分析器
    
    提供聚类分析功能。
    """
    
    def __init__(self, dataset: Optional[Dataset] = None):
        """初始化聚类分析器
        
        Args:
            dataset: 要分析的数据集，可选
        """
        super().__init__(dataset)
        self.model = None
        self.model_params = {}
        self.scaler = None
        
    def analyze(self, 
                features: List[str],
                method: ClusteringMethod = ClusteringMethod.KMEANS,
                n_clusters: int = 3,
                standardize: bool = True,
                include_charts: bool = True,
                **kwargs) -> AnalysisResult:
        """执行聚类分析
        
        Args:
            features: 用于聚类的特征列表
            method: 聚类方法
            n_clusters: 聚类数量（对于K-means和层次聚类）
            standardize: 是否标准化数据
            include_charts: 是否包含可视化图表
            **kwargs: 其他参数，包括：
                - eps: DBSCAN的邻域半径
                - min_samples: DBSCAN的最小样本数
                - linkage: 层次聚类的连接方法 ('ward', 'complete', 'average', 'single')
                - affinity: 层次聚类的距离度量 ('euclidean', 'manhattan', 'cosine')
                - n_components: 高斯混合模型的组件数
            
        Returns:
            AnalysisResult: 分析结果
            
        Raises:
            ValueError: 如果数据集无效或未设置
        """
        # 验证数据集
        self.validate_dataset()
        
        # 获取数据
        df = self.dataset.data
        
        # 验证列是否存在
        for feature in features:
            if feature not in df.columns:
                raise ValueError(f"列 '{feature}' 不存在于数据集中")
                
        # 只保留数值列
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if not all(feature in numeric_cols for feature in features):
            raise ValueError("所有特征必须是数值类型")
            
        # 去除缺失值
        data = df[features].dropna()
        
        # 标准化数据
        if standardize:
            self.scaler = StandardScaler()
            X = self.scaler.fit_transform(data)
        else:
            X = data.values
            
        # 根据聚类方法执行分析
        if method == ClusteringMethod.KMEANS:
            # K-means聚类
            result_data, model = self._kmeans_clustering(X, n_clusters, **kwargs)
        elif method == ClusteringMethod.HIERARCHICAL:
            # 层次聚类
            result_data, model = self._hierarchical_clustering(X, n_clusters, **kwargs)
        elif method == ClusteringMethod.DBSCAN:
            # DBSCAN聚类
            result_data, model = self._dbscan_clustering(X, **kwargs)
        elif method == ClusteringMethod.GAUSSIAN_MIXTURE:
            # 高斯混合模型
            result_data, model = self._gaussian_mixture(X, n_clusters, **kwargs)
        else:
            raise ValueError(f"不支持的聚类方法: {method}")
            
        # 保存模型
        self.model = model
        self.model_params = {
            'features': features,
            'method': method,
            'n_clusters': n_clusters,
            'standardize': standardize,
            **kwargs
        }
        
        # 添加聚类标签到原始数据
        data_with_clusters = data.copy()
        data_with_clusters['cluster'] = result_data['labels']
        
        # 创建元数据
        metadata = {
            'analysis_type': 'clustering',
            'clustering_method': method.name,
            'features': features,
            'n_clusters': n_clusters if method != ClusteringMethod.DBSCAN else result_data['n_clusters'],
            'standardize': standardize,
            'sample_size': len(data)
        }
        
        # 创建图表
        charts = []
        if include_charts:
            charts = self._create_charts(X, data, features, result_data, method)
            
        # 创建并返回结果
        return self._create_result(
            data=data_with_clusters,
            metadata=metadata,
            charts=charts
        )
        
    def _kmeans_clustering(self, X: np.ndarray, n_clusters: int, **kwargs) -> Tuple[Dict[str, Any], Any]:
        """执行K-means聚类
        
        Args:
            X: 特征矩阵
            n_clusters: 聚类数量
            **kwargs: 其他参数
            
        Returns:
            Tuple[Dict[str, Any], Any]: 结果数据和模型
        """
        from sklearn.cluster import KMeans
        
        # 设置参数
        random_state = kwargs.get('random_state', 42)
        max_iter = kwargs.get('max_iter', 300)
        n_init = kwargs.get('n_init', 10)
        
        # 创建并拟合模型
        model = KMeans(n_clusters=n_clusters, random_state=random_state, 
                      max_iter=max_iter, n_init=n_init)
        labels = model.fit_predict(X)
        
        # 计算轮廓系数
        from sklearn.metrics import silhouette_score
        silhouette_avg = silhouette_score(X, labels) if len(np.unique(labels)) > 1 else 0
        
        # 计算每个聚类的样本数量
        cluster_counts = np.bincount(labels)
        
        # 计算每个聚类的中心点
        centroids = model.cluster_centers_
        
        # 计算每个样本到其聚类中心的距离
        distances = np.sqrt(((X - centroids[labels]) ** 2).sum(axis=1))
        
        # 计算每个聚类的平均距离
        cluster_distances = []
        for i in range(n_clusters):
            mask = labels == i
            if np.any(mask):
                cluster_distances.append(np.mean(distances[mask]))
            else:
                cluster_distances.append(0)
                
        # 计算惯性（样本到最近聚类中心的距离平方和）
        inertia = model.inertia_
        
        # 创建结果数据
        result_data = {
            'labels': labels.tolist(),
            'centroids': centroids.tolist(),
            'silhouette_score': silhouette_avg,
            'inertia': inertia,
            'cluster_counts': cluster_counts.tolist(),
            'cluster_distances': cluster_distances,
            'n_clusters': n_clusters
        }
        
        return result_data, model
        
    def _hierarchical_clustering(self, X: np.ndarray, n_clusters: int, **kwargs) -> Tuple[Dict[str, Any], Any]:
        """执行层次聚类
        
        Args:
            X: 特征矩阵
            n_clusters: 聚类数量
            **kwargs: 其他参数
            
        Returns:
            Tuple[Dict[str, Any], Any]: 结果数据和模型
        """
        from sklearn.cluster import AgglomerativeClustering
        from scipy.cluster.hierarchy import dendrogram, linkage
        
        # 设置参数
        linkage_method = kwargs.get('linkage', 'ward')
        affinity = kwargs.get('affinity', 'euclidean')
        
        # 创建并拟合模型
        model = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage_method, affinity=affinity)
        labels = model.fit_predict(X)
        
        # 计算轮廓系数
        from sklearn.metrics import silhouette_score
        silhouette_avg = silhouette_score(X, labels) if len(np.unique(labels)) > 1 else 0
        
        # 计算每个聚类的样本数量
        cluster_counts = np.bincount(labels)
        
        # 计算聚类中心
        centroids = []
        for i in range(n_clusters):
            mask = labels == i
            if np.any(mask):
                centroids.append(X[mask].mean(axis=0))
            else:
                centroids.append(np.zeros(X.shape[1]))
        centroids = np.array(centroids)
        
        # 计算每个样本到其聚类中心的距离
        distances = np.sqrt(((X - centroids[labels]) ** 2).sum(axis=1))
        
        # 计算每个聚类的平均距离
        cluster_distances = []
        for i in range(n_clusters):
            mask = labels == i
            if np.any(mask):
                cluster_distances.append(np.mean(distances[mask]))
            else:
                cluster_distances.append(0)
                
        # 计算层次聚类的连接矩阵
        Z = linkage(X, method=linkage_method)
        
        # 创建结果数据
        result_data = {
            'labels': labels.tolist(),
            'centroids': centroids.tolist(),
            'silhouette_score': silhouette_avg,
            'cluster_counts': cluster_counts.tolist(),
            'cluster_distances': cluster_distances,
            'linkage_matrix': Z.tolist(),
            'n_clusters': n_clusters
        }
        
        return result_data, model
        
    def _dbscan_clustering(self, X: np.ndarray, **kwargs) -> Tuple[Dict[str, Any], Any]:
        """执行DBSCAN聚类
        
        Args:
            X: 特征矩阵
            **kwargs: 其他参数
            
        Returns:
            Tuple[Dict[str, Any], Any]: 结果数据和模型
        """
        from sklearn.cluster import DBSCAN
        
        # 设置参数
        eps = kwargs.get('eps', 0.5)
        min_samples = kwargs.get('min_samples', 5)
        
        # 创建并拟合模型
        model = DBSCAN(eps=eps, min_samples=min_samples)
        labels = model.fit_predict(X)
        
        # 获取聚类数量（不包括噪声点）
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        
        # 计算轮廓系数（如果有多个聚类且没有噪声点）
        from sklearn.metrics import silhouette_score
        if n_clusters > 1 and -1 not in labels:
            silhouette_avg = silhouette_score(X, labels)
        else:
            silhouette_avg = 0
            
        # 计算每个聚类的样本数量（包括噪声点）
        unique_labels = np.unique(labels)
        cluster_counts = {label: np.sum(labels == label) for label in unique_labels}
        
        # 计算聚类中心（不包括噪声点）
        centroids = []
        for label in unique_labels:
            if label != -1:  # 排除噪声点
                mask = labels == label
                if np.any(mask):
                    centroids.append(X[mask].mean(axis=0))
                    
        # 计算每个样本到其聚类中心的距离（不包括噪声点）
        distances = []
        for i, label in enumerate(labels):
            if label != -1:  # 排除噪声点
                centroid_idx = np.where(unique_labels == label)[0][0]
                if centroid_idx < len(centroids):
                    distance = np.sqrt(((X[i] - centroids[centroid_idx]) ** 2).sum())
                    distances.append(distance)
                    
        # 计算每个聚类的平均距离（不包括噪声点）
        cluster_distances = {}
        for label in unique_labels:
            if label != -1:  # 排除噪声点
                mask = labels == label
                if np.any(mask):
                    centroid_idx = np.where(unique_labels == label)[0][0]
                    if centroid_idx < len(centroids):
                        cluster_distances[label] = np.mean(
                            np.sqrt(((X[mask] - centroids[centroid_idx]) ** 2).sum(axis=1))
                        )
                        
        # 创建结果数据
        result_data = {
            'labels': labels.tolist(),
            'n_clusters': n_clusters,
            'silhouette_score': silhouette_avg,
            'cluster_counts': cluster_counts,
            'centroids': [c.tolist() for c in centroids] if centroids else [],
            'cluster_distances': cluster_distances,
            'eps': eps,
            'min_samples': min_samples,
            'noise_points': int(np.sum(labels == -1))
        }
        
        return result_data, model
        
    def _gaussian_mixture(self, X: np.ndarray, n_components: int, **kwargs) -> Tuple[Dict[str, Any], Any]:
        """执行高斯混合模型聚类
        
        Args:
            X: 特征矩阵
            n_components: 组件数量
            **kwargs: 其他参数
            
        Returns:
            Tuple[Dict[str, Any], Any]: 结果数据和模型
        """
        from sklearn.mixture import GaussianMixture
        
        # 设置参数
        random_state = kwargs.get('random_state', 42)
        covariance_type = kwargs.get('covariance_type', 'full')
        max_iter = kwargs.get('max_iter', 100)
        
        # 创建并拟合模型
        model = GaussianMixture(n_components=n_components, random_state=random_state,
                              covariance_type=covariance_type, max_iter=max_iter)
        model.fit(X)
        labels = model.predict(X)
        
        # 计算轮廓系数
        from sklearn.metrics import silhouette_score
        silhouette_avg = silhouette_score(X, labels) if len(np.unique(labels)) > 1 else 0
        
        # 计算每个聚类的样本数量
        cluster_counts = np.bincount(labels)
        
        # 获取聚类中心和协方差
        centroids = model.means_
        covariances = model.covariances_
        weights = model.weights_
        
        # 计算BIC和AIC
        bic = model.bic(X)
        aic = model.aic(X)
        
        # 计算每个样本的对数似然
        log_likelihood = model.score_samples(X)
        
        # 创建结果数据
        result_data = {
            'labels': labels.tolist(),
            'centroids': centroids.tolist(),
            'silhouette_score': silhouette_avg,
            'cluster_counts': cluster_counts.tolist(),
            'weights': weights.tolist(),
            'bic': bic,
            'aic': aic,
            'log_likelihood': log_likelihood.tolist(),
            'n_clusters': n_components
        }
        
        return result_data, model
        
    def _create_charts(self, X: np.ndarray, data: pd.DataFrame, features: List[str], 
                      result_data: Dict[str, Any], method: ClusteringMethod) -> List[Any]:
        """创建聚类分析图表
        
        Args:
            X: 特征矩阵
            data: 原始数据
            features: 特征列表
            result_data: 聚类结果数据
            method: 聚类方法
            
        Returns:
            List[Any]: 图表对象列表
        """
        charts = []
        labels = np.array(result_data['labels'])
        
        # 如果特征数量为2，创建二维散点图
        if len(features) == 2:
            scatter = ScatterChart(title=f"{features[0]} vs {features[1]} 聚类结果")
            scatter.set_data(X[:, 0], X[:, 1], c=labels)
            scatter.set_labels(x_label=features[0], y_label=features[1])
            charts.append(scatter)
            
            # 如果有聚类中心，添加到图表
            if 'centroids' in result_data and result_data['centroids']:
                centroids = np.array(result_data['centroids'])
                if centroids.shape[1] == 2:  # 确保中心点是二维的
                    centroid_scatter = ScatterChart(title=f"{features[0]} vs {features[1]} 聚类中心")
                    centroid_scatter.set_data(centroids[:, 0], centroids[:, 1])
                    centroid_scatter.set_labels(x_label=features[0], y_label=features[1])
                    charts.append(centroid_scatter)
                    
        # 如果特征数量为3，创建三维散点图
        elif len(features) == 3:
            # 创建三维散点图（使用matplotlib）
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            # 绘制数据点
            scatter = ax.scatter(X[:, 0], X[:, 1], X[:, 2], c=labels, cmap='viridis', s=50, alpha=0.6)
            
            # 如果有聚类中心，添加到图表
            if 'centroids' in result_data and result_data['centroids']:
                centroids = np.array(result_data['centroids'])
                if centroids.shape[1] == 3:  # 确保中心点是三维的
                    ax.scatter(centroids[:, 0], centroids[:, 1], centroids[:, 2], 
                              c='red', s=200, alpha=0.9, marker='X')
                    
            # 设置标签
            ax.set_xlabel(features[0])
            ax.set_ylabel(features[1])
            ax.set_zlabel(features[2])
            ax.set_title(f"{', '.join(features)} 聚类结果")
            
            # 添加颜色条
            plt.colorbar(scatter, ax=ax, label='聚类')
            
            # 保存图表
            import io
            import base64
            from scientific_analysis.visualization.base import BaseChart
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)
            
            # 创建自定义图表对象
            class CustomChart(BaseChart):
                def __init__(self, title, img_data):
                    super().__init__(title)
                    self.img_data = img_data
                    
                def plot(self):
                    return self.img_data
                    
            charts.append(CustomChart(f"{', '.join(features)} 聚类结果", img_str))
            
        # 创建聚类特征热图
        if len(features) > 1:
            # 计算每个聚类的特征均值
            cluster_means = {}
            for cluster in np.unique(labels):
                if cluster != -1:  # 排除DBSCAN的噪声点
                    cluster_means[f"聚类 {cluster}"] = data[features][labels == cluster].mean()
                    
            if cluster_means:
                # 创建热图数据
                heatmap_data = pd.DataFrame(cluster_means).T
                
                # 创建热图
                heatmap = HeatmapChart(title="聚类特征均值热图")
                heatmap.set_data(heatmap_data)
                charts.append(heatmap)
                
        # 对于层次聚类，创建树状图
        if method == ClusteringMethod.HIERARCHICAL and 'linkage_matrix' in result_data:
            # 创建树状图（使用matplotlib）
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # 绘制树状图
            Z = np.array(result_data['linkage_matrix'])
            dendrogram(Z, ax=ax, leaf_rotation=90)
            
            # 设置标题和标签
            ax.set_title("层次聚类树状图")
            ax.set_xlabel("样本索引")
            ax.set_ylabel("距离")
            
            # 保存图表
            import io
            import base64
            from scientific_analysis.visualization.base import BaseChart
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)
            
            # 创建自定义图表对象
            class CustomChart(BaseChart):
                def __init__(self, title, img_data):
                    super().__init__(title)
                    self.img_data = img_data
                    
                def plot(self):
                    return self.img_data
                    
            charts.append(CustomChart("层次聚类树状图", img_str))
            
        return charts
        
    def predict(self, new_data: Union[pd.DataFrame, Dict[str, Any]]) -> np.ndarray:
        """使用聚类模型进行预测
        
        Args:
            new_data: 新数据，可以是DataFrame或字典
            
        Returns:
            np.ndarray: 预测的聚类标签
            
        Raises:
            ValueError: 如果模型未训练或数据无效
        """
        if self.model is None:
            raise ValueError("模型未训练，请先调用analyze方法")
            
        # 获取模型参数
        features = self.model_params['features']
        standardize = self.model_params.get('standardize', True)
        
        # 将输入转换为DataFrame
        if isinstance(new_data, dict):
            new_data = pd.DataFrame([new_data])
            
        # 验证输入数据
        for feature in features:
            if feature not in new_data.columns:
                raise ValueError(f"输入数据缺少特征: {feature}")
                
        # 提取特征
        X = new_data[features].values
        
        # 标准化数据（如果原始分析使用了标准化）
        if standardize and self.scaler is not None:
            X = self.scaler.transform(X)
            
        # 根据聚类方法进行预测
        method = self.model_params['method']
        
        if method == ClusteringMethod.KMEANS:
            # K-means聚类
            return self.model.predict(X)
        elif method == ClusteringMethod.HIERARCHICAL:
            # 层次聚类（需要重新拟合，因为AgglomerativeClustering没有predict方法）
            from sklearn.metrics.pairwise import euclidean_distances
            
            # 获取原始聚类中心
            n_clusters = self.model_params['n_clusters']
            labels = self.model.labels_
            
            # 计算聚类中心
            centroids = []
            for i in range(n_clusters):
                mask = labels == i
                if np.any(mask):
                    centroids.append(self.model.fit_predict(X))
                    
            # 为每个新样本分配最近的聚类
            distances = euclidean_distances(X, centroids)
            return np.argmin(distances, axis=1)
        elif method == ClusteringMethod.DBSCAN:
            # DBSCAN（需要重新拟合，因为DBSCAN没有predict方法）
            from sklearn.metrics.pairwise import euclidean_distances
            
            # 获取原始聚类中心（排除噪声点）
            labels = self.model.labels_
            unique_labels = np.unique(labels)
            centroids = []
            
            # 计算每个聚类的中心
            for label in unique_labels:
                if label != -1:  # 排除噪声点
                    mask = labels == label
                    if np.any(mask):
                        centroids.append(np.mean(X[mask], axis=0))
                        
            if not centroids:
                # 如果没有有效的聚类，返回全部为噪声点
                return np.full(X.shape[0], -1)
                
            # 计算每个新样本到每个聚类中心的距离
            distances = euclidean_distances(X, centroids)
            
            # 获取DBSCAN参数
            eps = self.model_params.get('eps', 0.5)
            
            # 为每个新样本分配聚类
            min_distances = np.min(distances, axis=1)
            min_indices = np.argmin(distances, axis=1)
            
            # 如果最小距离大于eps，则为噪声点
            result = np.where(min_distances <= eps, min_indices, -1)
            return result
        elif method == ClusteringMethod.GAUSSIAN_MIXTURE:
            # 高斯混合模型
            return self.model.predict(X)
        else:
            raise ValueError(f"不支持的聚类方法: {method}")
            
    def evaluate_optimal_clusters(self, features: List[str], max_clusters: int = 10, 
                                method: ClusteringMethod = ClusteringMethod.KMEANS,
                                standardize: bool = True) -> Dict[str, Any]:
        """评估最佳聚类数量
        
        Args:
            features: 用于聚类的特征列表
            max_clusters: 最大聚类数量
            method: 聚类方法
            standardize: 是否标准化数据
            
        Returns:
            Dict[str, Any]: 评估结果
            
        Raises:
            ValueError: 如果数据集无效或未设置
        """
        # 验证数据集
        self.validate_dataset()
        
        # 获取数据
        df = self.dataset.data
        
        # 验证列是否存在
        for feature in features:
            if feature not in df.columns:
                raise ValueError(f"列 '{feature}' 不存在于数据集中")
                
        # 只保留数值列
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if not all(feature in numeric_cols for feature in features):
            raise ValueError("所有特征必须是数值类型")
            
        # 去除缺失值
        data = df[features].dropna()
        
        # 标准化数据
        if standardize:
            scaler = StandardScaler()
            X = scaler.fit_transform(data)
        else:
            X = data.values
            
        # 评估不同聚类数量
        if method == ClusteringMethod.KMEANS:
            return self._evaluate_kmeans(X, max_clusters)
        elif method == ClusteringMethod.HIERARCHICAL:
            return self._evaluate_hierarchical(X, max_clusters)
        elif method == ClusteringMethod.GAUSSIAN_MIXTURE:
            return self._evaluate_gaussian_mixture(X, max_clusters)
        else:
            raise ValueError(f"不支持的聚类方法评估: {method}")
            
    def _evaluate_kmeans(self, X: np.ndarray, max_clusters: int) -> Dict[str, Any]:
        """评估K-means聚类的最佳聚类数量
        
        Args:
            X: 特征矩阵
            max_clusters: 最大聚类数量
            
        Returns:
            Dict[str, Any]: 评估结果
        """
        from sklearn.cluster import KMeans
        from sklearn.metrics import silhouette_score
        
        # 初始化结果列表
        inertias = []
        silhouette_scores = []
        
        # 评估不同的聚类数量
        for n_clusters in range(2, max_clusters + 1):
            # 创建并拟合模型
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)
            
            # 计算惯性
            inertias.append(kmeans.inertia_)
            
            # 计算轮廓系数
            silhouette_avg = silhouette_score(X, labels) if len(np.unique(labels)) > 1 else 0
            silhouette_scores.append(silhouette_avg)
            
        # 创建评估结果
        result = {
            'n_clusters_range': list(range(2, max_clusters + 1)),
            'inertias': inertias,
            'silhouette_scores': silhouette_scores
        }
        
        # 创建肘部法则图表
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        # 绘制惯性（肘部法则）
        ax1.set_xlabel('聚类数量')
        ax1.set_ylabel('惯性', color='tab:blue')
        ax1.plot(result['n_clusters_range'], result['inertias'], 'o-', color='tab:blue')
        ax1.tick_params(axis='y', labelcolor='tab:blue')
        
        # 创建第二个y轴
        ax2 = ax1.twinx()
        ax2.set_ylabel('轮廓系数', color='tab:red')
        ax2.plot(result['n_clusters_range'], result['silhouette_scores'], 'o-', color='tab:red')
        ax2.tick_params(axis='y', labelcolor='tab:red')
        
        # 设置标题
        plt.title('K-means聚类评估：惯性和轮廓系数')
        plt.tight_layout()
        
        # 保存图表
        import io
        import base64
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        # 添加图表到结果
        result['elbow_plot'] = img_str
        
        return result
        
    def _evaluate_hierarchical(self, X: np.ndarray, max_clusters: int) -> Dict[str, Any]:
        """评估层次聚类的最佳聚类数量
        
        Args:
            X: 特征矩阵
            max_clusters: 最大聚类数量
            
        Returns:
            Dict[str, Any]: 评估结果
        """
        from sklearn.cluster import AgglomerativeClustering
        from sklearn.metrics import silhouette_score
        from scipy.cluster.hierarchy import dendrogram, linkage
        
        # 初始化结果列表
        silhouette_scores = []
        
        # 评估不同的聚类数量
        for n_clusters in range(2, max_clusters + 1):
            # 创建并拟合模型
            model = AgglomerativeClustering(n_clusters=n_clusters)
            labels = model.fit_predict(X)
            
            # 计算轮廓系数
            silhouette_avg = silhouette_score(X, labels) if len(np.unique(labels)) > 1 else 0
            silhouette_scores.append(silhouette_avg)
            
        # 计算层次聚类的连接矩阵
        Z = linkage(X, method='ward')
        
        # 创建评估结果
        result = {
            'n_clusters_range': list(range(2, max_clusters + 1)),
            'silhouette_scores': silhouette_scores,
            'linkage_matrix': Z.tolist()
        }
        
        # 创建轮廓系数图表
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 绘制轮廓系数
        ax.plot(result['n_clusters_range'], result['silhouette_scores'], 'o-')
        ax.set_xlabel('聚类数量')
        ax.set_ylabel('轮廓系数')
        ax.set_title('层次聚类评估：轮廓系数')
        plt.tight_layout()
        
        # 保存图表
        import io
        import base64
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        silhouette_plot = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        # 创建树状图
        fig, ax = plt.subplots(figsize=(12, 8))
        dendrogram(Z, ax=ax, leaf_rotation=90)
        ax.set_title("层次聚类树状图")
        ax.set_xlabel("样本索引")
        ax.set_ylabel("距离")
        plt.tight_layout()
        
        # 保存树状图
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        dendrogram_plot = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        # 添加图表到结果
        result['silhouette_plot'] = silhouette_plot
        result['dendrogram_plot'] = dendrogram_plot
        
        return result
        
    def _evaluate_gaussian_mixture(self, X: np.ndarray, max_clusters: int) -> Dict[str, Any]:
        """评估高斯混合模型的最佳聚类数量
        
        Args:
            X: 特征矩阵
            max_clusters: 最大聚类数量
            
        Returns:
            Dict[str, Any]: 评估结果
        """
        from sklearn.mixture import GaussianMixture
        from sklearn.metrics import silhouette_score
        
        # 初始化结果列表
        bic_scores = []
        aic_scores = []
        silhouette_scores = []
        
        # 评估不同的聚类数量
        for n_components in range(2, max_clusters + 1):
            # 创建并拟合模型
            model = GaussianMixture(n_components=n_components, random_state=42)
            model.fit(X)
            labels = model.predict(X)
            
            # 计算BIC和AIC
            bic_scores.append(model.bic(X))
            aic_scores.append(model.aic(X))
            
            # 计算轮廓系数
            silhouette_avg = silhouette_score(X, labels) if len(np.unique(labels)) > 1 else 0
            silhouette_scores.append(silhouette_avg)
            
        # 创建评估结果
        result = {
            'n_clusters_range': list(range(2, max_clusters + 1)),
            'bic_scores': bic_scores,
            'aic_scores': aic_scores,
            'silhouette_scores': silhouette_scores
        }
        
        # 创建BIC和AIC图表
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        # 绘制BIC
        ax1.set_xlabel('聚类数量')
        ax1.set_ylabel('BIC', color='tab:blue')
        ax1.plot(result['n_clusters_range'], result['bic_scores'], 'o-', color='tab:blue')
        ax1.tick_params(axis='y', labelcolor='tab:blue')
        
        # 创建第二个y轴
        ax2 = ax1.twinx()
        ax2.set_ylabel('AIC', color='tab:red')
        ax2.plot(result['n_clusters_range'], result['aic_scores'], 'o-', color='tab:red')
        ax2.tick_params(axis='y', labelcolor='tab:red')
        
        # 设置标题
        plt.title('高斯混合模型评估：BIC和AIC')
        plt.tight_layout()
        
        # 保存图表
        import io
        import base64
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        bic_aic_plot = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        # 创建轮廓系数图表
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 绘制轮廓系数
        ax.plot(result['n_clusters_range'], result['silhouette_scores'], 'o-')
        ax.set_xlabel('聚类数量')
        ax.set_ylabel('轮廓系数')
        ax.set_title('高斯混合模型评估：轮廓系数')
        plt.tight_layout()
        
        # 保存图表
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        silhouette_plot = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        # 添加图表到结果
        result['bic_aic_plot'] = bic_aic_plot
        result['silhouette_plot'] = silhouette_plot
        
        return result