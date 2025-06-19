# 设置 Python 路径
$env:PYTHONPATH = "."

# 激活虚拟环境
if (Test-Path "$PWD\\.venv\") {
    . "$PWD\\.venv\Scripts\Activate.ps1"
} else {
    Write-Host "正在创建虚拟环境..."
    python -m venv .venv
    . "$PWD\\.venv\Scripts\Activate.ps1"
    
    # 升级 pip
    python -m pip install --upgrade pip
    
    # 安装依赖
    Write-Host "正在安装依赖..."
    pip install -r requirements.txt
    
    # 安装开发依赖
    pip install sqlalchemy-utils
}

# 初始化数据库
Write-Host "正在初始化数据库..."
python -m scripts.init_db

# 启动应用
Write-Host "启动开发服务器..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
