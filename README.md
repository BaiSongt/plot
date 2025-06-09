# Scientific Analysis and Visualization Tool

一个基于 PySide6 的科学计算与可视化工具，提供数据导入/导出、科学计算、数据可视化、SCI 风格绘图、AI 报告生成和数据分析功能。

## 功能特点

- 📊 数据导入/导出（CSV, Excel, JSON, HDF5）
- 🔢 科学计算（线性代数、统计计算等）
- 📈 数据可视化（2D/3D 图表）
- 🎨 SCI 风格绘图
- 🤖 AI 报告生成
- 📊 高级数据分析

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
    utils/          # 工具函数
    data/           # 数据处理
    visualization/  # 可视化
    analysis/       # 分析功能
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
