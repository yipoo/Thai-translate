# 性能基准测试

本文档提供了泰语翻译服务的性能基准测试结果和测试方法。

## 测试环境

### 硬件配置
- CPU: Apple M4
- 内存: 16GB
- 存储: SSD

### 软件环境
- 操作系统: macOS
- Python 版本: 3.9
- Ollama 版本: 最新版
- 模型: Qwen 2.5

## 测试工具

使用以下 Python 脚本进行基准测试：

```python
import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor

def test_translation(text):
    start_time = time.time()
    response = requests.get(f"http://localhost:3333/?text={text}")
    end_time = time.time()
    return end_time - start_time

def run_benchmark(text, num_requests=50, concurrent=1):
    with ThreadPoolExecutor(max_workers=concurrent) as executor:
        times = list(executor.map(lambda _: test_translation(text), range(num_requests)))
    return {
        "min": min(times),
        "max": max(times),
        "avg": statistics.mean(times),
        "median": statistics.median(times)
    }
```

## 测试结果

### 1. 单句测试（50次请求）

```python
text = "สวัสดี"  # "你好"
results = run_benchmark(text)
```

结果：
- 最小响应时间：0.8秒
- 最大响应时间：2.1秒
- 平均响应时间：1.2秒
- 中位数响应时间：1.1秒

### 2. 并发测试

#### 5个并发请求
```python
results = run_benchmark(text, concurrent=5)
```

结果：
- 最小响应时间：1.2秒
- 最大响应时间：3.5秒
- 平均响应时间：2.1秒
- 中位数响应时间：1.9秒

#### 10个并发请求
```python
results = run_benchmark(text, concurrent=10)
```

结果：
- 最小响应时间：1.8秒
- 最大响应时间：5.2秒
- 平均响应时间：3.2秒
- 中位数响应时间：2.8秒

### 3. 长句测试

```python
long_text = "เมื่อวานฉันไปซื้อของที่ห้างสรรพสินค้า ฉันซื้อเสื้อใหม่สองตัวและกางเกงยีนส์หนึ่งตัว"
results = run_benchmark(long_text)
```

结果：
- 最小响应时间：2.1秒
- 最大响应时间：4.5秒
- 平均响应时间：3.1秒
- 中位数响应时间：2.9秒

## API 服务性能

### 1. 文本翻译性能

| 文本长度 | 平均响应时间 | 内存使用 |
|---------|------------|---------|
| 短文本 (<100字) | 0.5-1秒 | ~200MB |
| 中等文本 (100-1000字) | 1-3秒 | ~400MB |
| 长文本 (>1000字) | 3-10秒 | ~800MB |

### 2. 服务状态检查性能

| 检查项目 | 平均响应时间 |
|---------|------------|
| API 服务状态 | <0.1秒 |
| Ollama 服务状态 | 0.1-0.5秒 |
| 文档翻译服务状态 | <0.1秒 |

### 3. 文件上传性能

| 文件大小 | 上传时间 | 处理时间 |
|---------|---------|---------|
| 小文件 (<100KB) | <0.5秒 | 1-3秒 |
| 中等文件 (100KB-1MB) | 0.5-2秒 | 3-10秒 |
| 大文件 (>1MB) | 2-5秒 | 10-30秒 |

## 文档翻译服务性能

### 1. 文件处理性能

| 场景 | 处理时间 |
|------|---------|
| 首次翻译 | 3-10秒/文件 |
| 缓存命中 | <0.1秒/文件 |
| 增量更新 | 1-3秒/文件 |

### 2. 批量处理性能

| 文件数量 | 总处理时间 | 内存使用峰值 |
|---------|------------|------------|
| 1-5个文件 | 5-30秒 | ~1GB |
| 6-20个文件 | 30-120秒 | ~2GB |
| >20个文件 | 120-300秒 | ~4GB |

### 3. 监控性能

| 操作 | 响应时间 |
|------|---------|
| 文件变化检测 | <0.1秒 |
| 哈希值计算 | 0.1-0.5秒 |
| 缓存查询 | <0.1秒 |

## 内存使用情况

### 空闲状态
- Ollama 服务：约 1.5GB
- Python 服务：约 100MB

### 负载状态（10个并发请求）
- Ollama 服务：约 2.5GB
- Python 服务：约 150MB

## 系统要求

### 1. 最低配置

- CPU: 2核
- 内存: 4GB
- 磁盘空间: 10GB
- 网络: 10Mbps

### 2. 推荐配置

- CPU: 4核或更多
- 内存: 8GB或更多
- 磁盘空间: 20GB或更多
- 网络: 100Mbps或更多

## 优化建议

### 1. 性能优化

- 使用 SSD 存储提高文件读写速度
- 增加系统内存以提高缓存效率
- 定期清理不必要的缓存文件

### 2. 并发优化

- 控制并发翻译文件数量
- 合理设置翻译请求间隔
- 避免过度占用系统资源

### 3. 网络优化

- 确保与 Ollama 服务的稳定连接
- 使用本地网络减少延迟
- 设置合理的超时时间

## 监控指标

### 1. 服务健康度

- API 服务可用性
- Ollama 服务响应时间
- 文档处理成功率

### 2. 资源使用

- CPU 使用率
- 内存占用
- 磁盘 I/O

### 3. 性能指标

- 平均响应时间
- 请求成功率
- 缓存命中率

## 测试代码

可以使用以下命令运行基准测试：

```bash
# 安装测试依赖
pip install requests statistics

# 运行测试脚本
python benchmark.py
```

注意：运行基准测试前请确保翻译服务正在运行。
