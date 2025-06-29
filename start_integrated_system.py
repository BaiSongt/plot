#!/usr/bin/env python3
"""
整合数据分析软件启动脚本
支持多种启动模式：Web模式、桌面模式、完整模式
"""

import os
import sys
import subprocess
import argparse
import time
import threading
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

def start_backend():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    backend_dir = PROJECT_ROOT / "backend"
    
    # 检查虚拟环境
    venv_path = PROJECT_ROOT / ".venv"
    if venv_path.exists():
        if sys.platform == "win32":
            python_exe = venv_path / "Scripts" / "python.exe"
            activate_script = venv_path / "Scripts" / "activate.ps1"
        else:
            python_exe = venv_path / "bin" / "python"
            activate_script = venv_path / "bin" / "activate"
    else:
        python_exe = "python"
    
    # 启动后端
    cmd = [
        str(python_exe), "-m", "uvicorn", 
        "app.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ]
    
    return subprocess.Popen(
        cmd, 
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def start_frontend():
    """启动前端服务"""
    print("🌐 启动前端服务...")
    frontend_dir = PROJECT_ROOT / "frontend"
    
    # 检查node_modules
    if not (frontend_dir / "node_modules").exists():
        print("📦 安装前端依赖...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
    
    # 启动前端开发服务器
    cmd = ["npm", "run", "dev"]
    
    return subprocess.Popen(
        cmd,
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def start_desktop():
    """启动桌面应用"""
    print("🖥️ 启动桌面应用...")
    
    # 检查虚拟环境
    venv_path = PROJECT_ROOT / ".venv"
    if venv_path.exists():
        if sys.platform == "win32":
            python_exe = venv_path / "Scripts" / "python.exe"
        else:
            python_exe = venv_path / "bin" / "python"
    else:
        python_exe = "python"
    
    # 启动桌面应用
    cmd = [str(python_exe), "src/scientific_analysis/main.py"]
    
    return subprocess.Popen(
        cmd,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def check_dependencies():
    """检查依赖是否安装"""
    print("🔍 检查依赖...")
    
    # 检查Python依赖
    try:
        import fastapi
        import uvicorn
        import PySide6
        print("✅ Python依赖检查通过")
    except ImportError as e:
        print(f"❌ Python依赖缺失: {e}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    # 检查Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js版本: {result.stdout.strip()}")
        else:
            print("❌ Node.js未安装")
            return False
    except FileNotFoundError:
        print("❌ Node.js未安装")
        return False
    
    return True

def wait_for_service(url, timeout=30):
    """等待服务启动"""
    import requests
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def main():
    parser = argparse.ArgumentParser(description="启动整合数据分析软件")
    parser.add_argument(
        "--mode", 
        choices=["web", "desktop", "full", "backend-only"],
        default="full",
        help="启动模式"
    )
    parser.add_argument(
        "--check-deps", 
        action="store_true",
        help="检查依赖"
    )
    
    args = parser.parse_args()
    
    if args.check_deps:
        if not check_dependencies():
            sys.exit(1)
        return
    
    print("🎯 整合数据分析软件启动器")
    print(f"📋 启动模式: {args.mode}")
    
    processes = []
    
    try:
        if args.mode in ["web", "full", "backend-only"]:
            # 启动后端
            backend_process = start_backend()
            processes.append(("后端", backend_process))
            
            # 等待后端启动
            print("⏳ 等待后端服务启动...")
            if wait_for_service("http://localhost:8000"):
                print("✅ 后端服务启动成功")
            else:
                print("❌ 后端服务启动失败")
        
        if args.mode in ["web", "full"]:
            # 启动前端
            frontend_process = start_frontend()
            processes.append(("前端", frontend_process))
            
            # 等待前端启动
            print("⏳ 等待前端服务启动...")
            time.sleep(5)  # 前端需要更长时间启动
            if wait_for_service("http://localhost:5173"):
                print("✅ 前端服务启动成功")
                print("🌐 Web界面: http://localhost:5173")
            else:
                print("❌ 前端服务启动失败")
        
        if args.mode in ["desktop", "full"]:
            # 启动桌面应用
            desktop_process = start_desktop()
            processes.append(("桌面应用", desktop_process))
            print("✅ 桌面应用启动成功")
        
        if args.mode != "backend-only":
            print("\n🎉 系统启动完成!")
            print("📊 后端API: http://localhost:8000")
            print("📚 API文档: http://localhost:8000/docs")
            if args.mode in ["web", "full"]:
                print("🌐 Web界面: http://localhost:5173")
            
            print("\n按 Ctrl+C 停止所有服务")
        
        # 等待用户中断
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        
        for name, process in processes:
            print(f"⏹️ 停止{name}...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        print("✅ 所有服务已停止")

if __name__ == "__main__":
    main()