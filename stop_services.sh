#!/bin/bash

# 确保在脚本所在目录执行
cd "$(dirname "$0")"

# 停止 API 服务
if [ -f logs/api.pid ]; then
    API_PID=$(cat logs/api.pid)
    if ps -p $API_PID > /dev/null; then
        echo "停止 API 服务 (PID: $API_PID)..."
        kill $API_PID
    fi
    rm logs/api.pid
fi

# 停止文档翻译服务
if [ -f logs/translator.pid ]; then
    TRANSLATOR_PID=$(cat logs/translator.pid)
    if ps -p $TRANSLATOR_PID > /dev/null; then
        echo "停止文档翻译服务 (PID: $TRANSLATOR_PID)..."
        kill $TRANSLATOR_PID
    fi
    rm logs/translator.pid
fi

echo "所有服务已停止"
