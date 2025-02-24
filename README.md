# 泰语翻译服务

一个基于 Ollama 的泰语到中文的翻译服务。本服务使用 FastAPI 构建 API 接口，通过 Ollama 的 Qwen 2.5 模型提供高质量的翻译。

## 功能特点

- API 接口翻译
- 文档批量翻译
- 实时文件监控
- 自动编码检测

## 环境要求

- Python 3.9+
- Ollama
- qwen2.5 模型

## 安装步骤

### 1. 安装 Ollama

macOS 用户可以使用 Homebrew 安装：

```bash
brew install ollama
```

或访问 [Ollama 官网](https://ollama.ai) 下载安装包。

### 2. 下载并运行 Qwen 2.5 模型

安装完 Ollama 后，运行以下命令下载模型：

```bash
ollama pull qwen2.5
```

### 3. 配置 Python 环境

1. 创建并激活虚拟环境：

```bash
python3.9 -m venv venv
source venv/bin/activate
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

## 使用方式

### 1. API 服务

1. 启动 Ollama 服务：

```bash
ollama serve
```

2. 在新的终端窗口中，启动翻译服务：

```bash
source venv/bin/activate
python3.9 main.py
```

服务将在 http://localhost:3333 上运行。

#### API 使用示例

```bash
curl "http://localhost:3333/?text=สวัสดี"
```

### 2. 文档翻译

1. 确保 API 服务正在运行

2. 在新的终端窗口中，启动文档翻译服务：

```bash
source venv/bin/activate
python3.9 document_translator.py
```

3. 使用方法：
   - 将泰语文本文件(.txt)放入 `input_docs` 目录
   - 翻译后的文件会自动保存到 `output_docs` 目录
   - 文件名格式：`translated_原文件名.txt`

#### 文档翻译特点

- 自动检测文件编码
- 按段落翻译
- 实时监控新文件
- 自动处理已有文件

## 项目结构

```
Thai-translate/
├── main.py              # API 服务主程序
├── document_translator.py # 文档翻译程序
├── requirements.txt     # 项目依赖
├── input_docs/         # 待翻译文档目录
├── output_docs/        # 翻译结果目录
└── docs/              # 文档目录
    ├── usage_examples.md
    └── benchmark.md
```

## 故障排除

1. 如果遇到端口被占用的错误：
```bash
lsof -i :3333  # 查看占用端口的进程
kill -9 <PID>  # 结束占用端口的进程
```

2. 如果 Ollama 服务无响应：
```bash
# 重启 Ollama 服务
pkill ollama
ollama serve
```

3. 如果文档翻译出错：
- 检查文件编码是否支持
- 确保 API 服务正在运行
- 查看日志输出了解详细错误信息

## 注意事项

- 确保在使用服务前 Ollama 服务已经启动
- 翻译服务会自动过滤掉解释性文字和英文内容
- 建议使用 UTF-8 编码的文本文件
- 大文件翻译时会自动添加延时，避免请求过快
- 文档翻译支持实时监控，无需重启服务

## 技术栈

- FastAPI: Web 框架
- Ollama: 本地大语言模型服务
- Qwen 2.5: 翻译模型
- Python 3.9: 运行环境
- Watchdog: 文件系统监控
- Chardet: 编码检测
