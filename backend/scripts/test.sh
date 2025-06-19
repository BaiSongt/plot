#!/bin/bash

# 设置 Python 路径
export PYTHONPATH="."

# 激活虚拟环境
if [ -d "$PWD/.venv" ]; then
    source "$PWD/.venv/bin/activate"
else
    echo "错误: 虚拟环境未找到，请先运行 start.sh 或 start.ps1 脚本。"
    exit 1
fi

# 运行测试
echo "运行测试..."
pytest tests/ -v --cov=app --cov-report=term-missing

# 检查测试结果
if [ $? -eq 0 ]; then
    echo "测试通过!"
else
    echo "测试失败!"
    exit 1
fi
