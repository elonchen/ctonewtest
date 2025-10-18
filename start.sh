#!/bin/bash

# 本地 OpenAI 兼容 API 启动脚本

echo "================================================"
echo "  本地 OpenAI 兼容 API 服务"
echo "================================================"
echo ""

# 检查 Python 版本
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python 版本: $PYTHON_VERSION"

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -q -r requirements.txt

echo ""
echo "================================================"
echo "  启动服务器"
echo "================================================"
echo ""

# 加载环境变量（如果存在 .env 文件）
if [ -f ".env" ]; then
    echo "✓ 加载 .env 配置文件"
    export $(cat .env | grep -v '^#' | xargs)
fi

# 设置默认值
export API_KEY=${API_KEY:-sk-local-test-key}
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-8000}

echo "配置信息:"
echo "  - API Key: $API_KEY"
echo "  - Host: $HOST"
echo "  - Port: $PORT"
echo ""
echo "启动服务器..."
echo "  - API 文档: http://localhost:$PORT/docs"
echo "  - API 地址: http://localhost:$PORT"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 启动服务器
python main.py
