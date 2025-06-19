# Scientific Analysis and Visualization Tool

一个基于 PySide6 的科学计算与可视化工具，提供数据导入/导出、科学计算、数据可视化、SCI 风格绘图、AI 报告生成和数据分析功能。新增了描述性统计、相关性分析、回归分析和聚类分析等高级分析功能，以及丰富的可视化图表支持。

## 功能特点

- 📊 数据导入/导出（CSV, Excel, JSON, HDF5, Parquet, Feather）
- 🔢 科学计算（线性代数、统计计算等）
- 📈 数据可视化（2D/3D 图表、交互式图表）
- 🎨 SCI 风格绘图
- 🤖 AI 报告生成
- 📊 高级数据分析
- 📋 描述性统计（基本统计量、分布统计、频率表、异常值检测）
- 🔄 相关性分析（相关系数计算、相关性矩阵、热图）
- 📉 回归分析（线性回归、多项式回归、多元线性回归）
- 🧩 聚类分析（K-means、层次聚类、DBSCAN、高斯混合模型）

## 安装

1. 克隆仓库：
   ```bash
   git clone https://github.com/BaiSongt/scientific-analysis-tool.git
   cd scientific-analysis-tool
   ```

2. 创建并激活虚拟环境（推荐）：
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 使用

```bash
python -m scientific_analysis
```

## 项目结构

```
src/
  scientific_analysis/
    __init__.py
    main.py          # 主程序入口
    core/           # 核心功能
    ui/             # 用户界面
      main_window.py      # 主窗口
      visualization_panel.py  # 可视化面板
      analysis_panel.py   # 分析面板
    utils/          # 工具函数
    data/           # 数据处理
      manager.py         # 数据管理器
      preprocessing.py   # 数据预处理
      io.py             # 数据导入导出
    models/         # 数据模型
      dataset.py        # 数据集模型
    analysis/       # 分析模块
      descriptive.py    # 描述性统计
      correlation.py    # 相关性分析
      regression.py     # 回归分析
      clustering.py     # 聚类分析
    visualization/  # 可视化模块
    models/         # 数据模型
```

## 开发

1. 安装开发依赖：
   ```bash
   pip install -e ".[dev]"
   ```

2. 运行测试：
   ```bash
   pytest
   ```

## 贡献

欢迎提交 Issue 和 Pull Request。

## 许可证

[MIT](LICENSE)
