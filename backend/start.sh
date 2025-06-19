#!/bin/bash

# 设置 Python 路径
export PYTHONPATH="."

# 激活虚拟环境
if [ -d "$PWD/.venv" ]; then
    source "$PWD/.venv/bin/activate"
else
    echo "正在创建虚拟环境..."
    python -m venv .venv
    source "$PWD/.venv/bin/activate"
    
    # 升级 pip
    python -m pip install --upgrade pip
    
    # 安装依赖
    echo "正在安装依赖..."
    pip install -r requirements.txt
    
    # 安装开发依赖
    pip install sqlalchemy-utils
fi

# 初始化数据库
echo "正在初始化数据库..."
python -m scripts.init_db

# 启动应用
echo "启动开发服务器..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
