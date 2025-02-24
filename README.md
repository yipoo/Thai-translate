# 泰语翻译服务

基于 FastAPI 和 Ollama (Qwen 2.5) 的泰语到中文翻译服务，提供 Web 界面、API 接口和文档批量翻译功能。

## 主要功能

- 🌐 **Web 界面**：直观的用户界面，支持文件上传和服务状态监控
- 🚀 **API 接口**：简单易用的 RESTful API
- 📝 **文档翻译**：支持批量文档翻译，自动检测文件变化
- 💾 **智能缓存**：避免重复翻译相同内容
- 📊 **服务监控**：实时监控所有服务组件状态

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖包
pip install -r requirements.txt

# 确保已安装 Ollama 并运行 qwen2.5 模型
ollama run qwen2.5
```

### 2. 启动服务

使用启动脚本一键启动所有服务：

```bash
./start_services.sh
```

服务启动后：
- Web 界面：访问 http://localhost:3333
- API 服务：监听 http://localhost:3333
- 文档翻译服务：自动监控 input_docs 目录

停止服务：

```bash
./stop_services.sh
```

## 使用方法

### 1. Web 界面

访问 http://localhost:3333 可以：
- 查看所有服务的实时状态
- 上传泰语文档进行翻译
- 监控翻译进度

### 2. API 接口

```bash
# 文本翻译
curl "http://localhost:3333/api/translate?text=สวัสดี"

# 查看服务状态
curl "http://localhost:3333/api/status"

# 上传文档
curl -X POST "http://localhost:3333/api/upload" -F "file=@your_file.txt"
```

### 3. 文档翻译

两种使用方式：
1. 通过 Web 界面上传文件
2. 直接将文件放入 `input_docs` 目录

翻译结果将自动保存到 `output_docs` 目录。

## 项目结构

```
Thai-translate/
├── main.py                # API 服务主程序
├── document_translator.py # 文档翻译服务
├── start_services.sh     # 服务启动脚本
├── stop_services.sh      # 服务停止脚本
├── requirements.txt      # Python 依赖
├── static/              # Web 界面文件
├── input_docs/          # 待翻译文档目录
├── output_docs/         # 翻译结果目录
├── logs/               # 服务日志目录
└── .translation_cache/  # 翻译缓存目录
```

## 配置说明

### 1. 服务端口
- API 服务：3333
- Ollama 服务：11434（默认）

### 2. 目录说明
- `input_docs`：放置待翻译的泰语文档
- `output_docs`：存放翻译完成的文档
- `logs`：服务日志文件
- `.translation_cache`：翻译缓存，避免重复翻译

## 注意事项

1. 文件上传：
   - 仅支持包含泰语的文本文件
   - 自动检测文件编码
   - 建议单个文件不超过 1MB

2. 服务状态：
   - 使用 Web 界面监控服务状态
   - 查看 `logs` 目录下的日志文件排查问题

3. 性能优化：
   - 使用缓存避免重复翻译
   - 自动管理翻译队列
   - 支持并发处理多个文件

## 故障排除

1. 服务无法启动
   - 检查 Python 虚拟环境是否激活
   - 确认 Ollama 服务是否运行
   - 查看日志文件获取详细错误信息

2. 翻译失败
   - 确保文件包含泰语文本
   - 检查文件编码是否正确
   - 验证网络连接是否正常

3. 性能问题
   - 清理不需要的缓存文件
   - 避免同时处理过多文件
   - 确保系统资源充足

## 更多信息

- 详细使用示例：查看 `docs/usage_examples.md`
- 性能测试报告：查看 `docs/benchmark.md`
- API 文档：访问 http://localhost:3333/docs
