# 科学分析与可视化工具开发指南

## 代码风格规范

### Python 代码风格

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 编码规范
- 使用 4 个空格进行缩进，不使用制表符
- 行长度限制在 88 个字符以内（使用 Black 格式化工具的默认值）
- 使用 snake_case 命名变量和函数
- 使用 CamelCase 命名类
- 使用 UPPER_CASE 命名常量
- 模块导入顺序：标准库 > 第三方库 > 本地模块，每组之间空一行

### 文档字符串规范

使用 [NumPy 风格](https://numpydoc.readthedocs.io/en/latest/format.html)的文档字符串：

```python
def function_name(param1, param2, param3=None):
    """
    简短描述

    详细描述（可选）

    Parameters
    ----------
    param1 : type
        参数1的描述
    param2 : type
        参数2的描述
    param3 : type, optional
        参数3的描述，默认为None

    Returns
    -------
    type
        返回值的描述

    Raises
    ------
    ExceptionType
        异常的描述

    Examples
    --------
    >>> function_name(1, 2)
    3
    """
```

### 代码注释

- 使用注释解释"为什么"而不是"是什么"（代码本身应该清晰地表达"是什么"）
- 对于复杂的算法或不直观的解决方案，添加详细注释
- 使用 TODO, FIXME, NOTE 等标记注释需要后续处理的代码

### 代码格式化工具

使用以下工具保持代码风格一致：

- [Black](https://black.readthedocs.io/): 代码格式化
- [isort](https://pycqa.github.io/isort/): 导入语句排序
- [flake8](https://flake8.pycqa.org/): 代码风格检查
- [mypy](http://mypy-lang.org/): 类型检查

## 项目结构规范

### 模块组织

```
src/scientific_analysis/
├── __init__.py           # 包初始化
├── main.py               # 应用入口点
├── config.py             # 配置管理
├── core/                 # 核心功能
├── data/                 # 数据处理模块
│   ├── __init__.py
│   ├── io.py             # 数据导入导出
│   ├── preprocessing.py  # 数据预处理
│   └── manager.py        # 数据管理
├── models/               # 数据模型
│   ├── __init__.py
│   └── dataset.py        # 数据集模型
├── analysis/             # 分析模块
│   ├── __init__.py
│   ├── base.py           # 分析基类
│   ├── descriptive.py    # 描述性统计
│   ├── correlation.py    # 相关性分析
│   ├── regression.py     # 回归分析
│   └── clustering.py     # 聚类分析
├── visualization/        # 可视化模块
│   ├── __init__.py
│   ├── base.py           # 可视化基类
│   ├── charts.py         # 基本图表
│   ├── style.py          # 样式管理
│   ├── export.py         # 导出功能
│   ├── sci_style/        # SCI风格图表
│   └── three_d/          # 3D可视化
├── ui/                   # 用户界面
│   ├── __init__.py
│   ├── main_window.py    # 主窗口
│   ├── data_widgets.py   # 数据相关组件
│   ├── analysis_widgets.py # 分析相关组件
│   ├── visualization_widgets.py # 可视化相关组件
│   └── dialogs.py        # 对话框
├── utils/                # 工具函数
│   ├── __init__.py
│   └── helpers.py        # 辅助函数
└── resources/            # 资源文件
    ├── icons/            # 图标
    ├── styles/           # 样式表
    └── templates/        # 模板
```

### 测试结构

```
tests/
├── conftest.py           # 测试配置和共享夹具
├── test_data/            # 测试数据
├── test_preprocessing.py # 数据预处理测试
├── test_io.py            # 数据IO测试
├── test_analysis.py      # 分析模块测试
├── test_visualization.py # 可视化模块测试
└── test_ui.py            # UI组件测试
```

## 开发最佳实践

### 错误处理

- 使用明确的异常类型，避免捕获所有异常
- 提供有意义的错误消息
- 在适当的抽象级别处理异常
- 使用日志记录异常，而不仅仅是打印

```python
try:
    # 可能引发异常的代码
    data = load_file(file_path)
except FileNotFoundError:
    logger.error(f"文件未找到: {file_path}")
    # 处理错误
except PermissionError:
    logger.error(f"没有权限访问文件: {file_path}")
    # 处理错误
except Exception as e:
    logger.exception(f"加载文件时发生未预期的错误: {str(e)}")
    # 处理错误
```

### 日志记录

- 使用 Python 的 `logging` 模块进行日志记录
- 为每个模块创建命名的日志记录器
- 使用适当的日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- 包含上下文信息以便于调试

```python
import logging

# 创建命名的日志记录器
logger = logging.getLogger(__name__)

def process_data(data):
    logger.info(f"开始处理数据，形状: {data.shape}")
    try:
        # 处理数据
        result = perform_calculation(data)
        logger.debug(f"计算结果: {result}")
        return result
    except ValueError as e:
        logger.error(f"数据处理错误: {str(e)}")
        raise
```

### 性能优化

- 使用性能分析工具（如 cProfile, line_profiler）识别瓶颈
- 优先使用向量化操作（NumPy, Pandas）而不是循环
- 对于大数据集，考虑使用惰性求值和流处理
- 使用适当的数据结构和算法
- 仅在必要时进行优化，避免过早优化

### 内存管理

- 处理大型数据集时注意内存使用
- 使用生成器和迭代器处理大型数据流
- 及时释放不再需要的大型对象
- 考虑使用内存映射文件处理超大数据集

### 并发处理

- 使用 `concurrent.futures` 或 `multiprocessing` 进行并行计算
- 使用线程池处理IO密集型任务
- 使用进程池处理CPU密集型任务
- 注意线程安全和资源竞争问题

### 用户界面开发

- 遵循 Qt/PySide6 的最佳实践
- 使用信号和槽机制进行组件通信
- 将UI逻辑与业务逻辑分离
- 使用模型-视图架构处理数据显示
- 确保UI响应性，将耗时操作放在后台线程中

## 文档规范

### 代码文档

- 为所有公共API提供完整的文档字符串
- 使用类型注解提高代码可读性和IDE支持
- 为复杂的算法和工作流程添加流程图或说明

### 用户文档

- 提供安装和设置指南
- 编写功能使用教程和示例
- 包含常见问题解答（FAQ）
- 使用截图和图表说明功能

### 开发者文档

- 提供架构概述和设计决策说明
- 包含模块依赖关系图
- 说明如何扩展和定制功能
- 提供API参考文档

## 测试规范

### 单元测试

- 使用 pytest 框架
- 为每个功能模块编写测试
- 使用参数化测试覆盖多种情况
- 使用模拟对象（mock）隔离依赖

### 集成测试

- 测试模块之间的交互
- 验证数据流和工作流程
- 测试边界条件和错误处理

### UI测试

- 使用 Qt Test 框架测试UI组件
- 验证用户交互和事件处理
- 测试UI状态和数据绑定

## 版本控制和发布

### 版本控制

- 遵循 Git 工作流程和提交规范（见 git_workflow.md）
- 使用语义化版本号
- 维护更新日志（CHANGELOG.md）

### 发布流程

- 在发布前运行完整的测试套件
- 更新版本号和更新日志
- 创建发布分支和标签
- 构建分发包（wheel, sdist）
- 更新文档和发布说明

## 安全最佳实践

- 不要在代码中硬编码敏感信息（密码、API密钥等）
- 使用环境变量或配置文件存储敏感信息
- 验证和清理用户输入
- 使用安全的依赖项，定期更新
- 遵循最小权限原则

## 性能和可扩展性考虑

- 设计时考虑未来的扩展性
- 使用插件架构允许功能扩展
- 优化关键路径上的性能
- 考虑大数据集的处理能力
- 设计时考虑多用户和并发使用场景