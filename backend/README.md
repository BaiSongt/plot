# Plot 数据可视化平台 - 后端

## 项目结构

```
backend/
├── app/
│   ├── api/                    # API 路由
│   │   ├── endpoints/          # API 端点
│   │   └── api_v1/             # API 版本
│   ├── core/                   # 核心配置
│   ├── db/                     # 数据库相关
│   │   └── migrations/         # 数据库迁移
│   ├── models/                 # 数据库模型
│   ├── schemas/                # Pydantic 模型
│   ├── __init__.py
│   └── main.py                 # FastAPI 应用入口
├── tests/                      # 测试代码
├── .env                        # 环境变量
├── .gitignore
├── alembic.ini                 # Alembic 配置
├── requirements.txt            # Python 依赖
├── start.ps1                  # Windows 启动脚本
└── start.sh                   # Linux/macOS 启动脚本
```

## 环境要求

- Python 3.9+
- PostgreSQL / SQLite
- uv (推荐) 或 pip

## 快速开始

### 1. 克隆仓库

```bash
git clone <repository-url>
cd plot/backend
```

### 2. 创建并激活虚拟环境

使用 `uv` (推荐):

```bash
uv venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS
```

或使用 Python 内置 venv:

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS
```

### 3. 安装依赖

使用 `uv` (推荐):

```bash
uv pip install -r requirements.txt
```

或使用 pip:

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并根据需要修改配置。

### 5. 初始化数据库

```bash
alembic upgrade head
python -m app.db.init_db
```

### 6. 启动开发服务器

Windows:

```bash
.\start.ps1
```

Linux/macOS:

```bash
chmod +x start.sh
./start.sh
```

或者直接使用 uvicorn:

```bash
uvicorn app.main:app --reload
```

### 7. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 文档

API 文档使用 OpenAPI 3.0 规范，可以通过以下方式访问：

- `/docs` - Swagger UI 交互式文档
- `/redoc` - ReDoc 文档
- `/openapi.json` - OpenAPI 规范 JSON

## 开发

### 创建数据库迁移

```bash
alembic revision --autogenerate -m "Your migration message"
alembic upgrade head
```

### 运行测试

```bash
pytest
```

### 代码风格

项目使用以下工具保持代码风格一致：

- Black - 代码格式化
- isort - 导入排序
- flake8 - 代码检查

在提交代码前运行：

```bash
black .
isort .
flake8
```

## 生产部署

### 使用 Gunicorn (推荐用于生产)

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

### 使用 Docker

1. 构建镜像:

```bash
docker build -t plot-backend .
```

2. 运行容器:

```bash
docker run -d --name plot-backend -p 8000:8000 plot-backend
```

## 贡献

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

[MIT](LICENSE)
