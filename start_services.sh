#!/bin/bash

# 确保在脚本所在目录执行
cd "$(dirname "$0")"

# 激活虚拟环境
source venv/bin/activate

# 检查 Ollama 服务
echo "检查 Ollama 服务..."
if ! curl -s "http://localhost:11434/api/version" > /dev/null; then
    echo "警告: Ollama 服务似乎没有运行"
    echo "请确保已安装 Ollama 并运行 'ollama run qwen2.5'"
    exit 1
fi

# 创建日志目录
mkdir -p logs

# 启动文档翻译服务
echo "启动文档翻译服务..."
python3.9 document_translator.py > logs/document_translator.log 2>&1 &
TRANSLATOR_PID=$!
echo "文档翻译服务已启动 (PID: $TRANSLATOR_PID)"

# 等待几秒确保文档翻译服务启动
sleep 2

# 启动 API 服务
echo "启动 API 服务..."
python3.9 main.py > logs/api.log 2>&1 &
API_PID=$!
echo "API 服务已启动 (PID: $API_PID)"

# 保存进程 ID
echo $TRANSLATOR_PID > logs/document_translator.pid
echo $API_PID > logs/api.pid

echo "所有服务已启动！"
echo "- API 服务日志: logs/api.log"
echo "- 文档翻译服务日志: logs/document_translator.log"
echo "访问 http://localhost:3333 使用 Web 界面"

# 等待用户按 Ctrl+C
echo "按 Ctrl+C 停止所有服务..."
trap "kill $TRANSLATOR_PID $API_PID; exit" INT
wait
