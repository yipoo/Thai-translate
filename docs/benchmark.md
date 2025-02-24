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

## 内存使用情况

### 空闲状态
- Ollama 服务：约 1.5GB
- Python 服务：约 100MB

### 负载状态（10个并发请求）
- Ollama 服务：约 2.5GB
- Python 服务：约 150MB

## 优化建议

1. **系统层面**
   - 使用 SSD 存储
   - 确保足够的内存（建议 16GB 以上）
   - 保持系统资源充足

2. **应用层面**
   - 实现请求队列管理
   - 添加结果缓存
   - 限制最大并发数

3. **网络层面**
   - 使用本地回环地址减少网络延迟
   - 考虑使用 Unix Socket 代替 TCP/IP

## 测试代码

可以使用以下命令运行基准测试：

```bash
# 安装测试依赖
pip install requests statistics

# 运行测试脚本
python benchmark.py
```

注意：运行基准测试前请确保翻译服务正在运行。
