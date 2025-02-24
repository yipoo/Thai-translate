from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
import os
import chardet
import re
import aiofiles
from datetime import datetime, timedelta
import logging
import requests
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import psutil
import time
from typing import List
import json

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 添加静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def contains_thai_text(text):
    # 泰语 Unicode 范围：\u0E00-\u0E7F
    thai_pattern = re.compile(r'[\u0E00-\u0E7F]')
    return bool(thai_pattern.search(text))

def get_file_encoding(file_content):
    result = chardet.detect(file_content)
    return result['encoding']

@app.get("/api/status")
async def check_status():
    try:
        status = {
            "api_service": "stopped",
            "ollama_service": "stopped",
            "document_service": "stopped"
        }
        
        # 检查 API 服务状态（当前进程）
        current_pid = os.getpid()
        if psutil.pid_exists(current_pid):
            api_process = psutil.Process(current_pid)
            if api_process.status() != psutil.STATUS_ZOMBIE:
                status["api_service"] = "running"
        
        # 检查 Ollama 服务状态
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                status["ollama_service"] = "running"
        except:
            pass
        
        # 检查文档翻译服务状态
        pid_file = "document_translator.pid"
        if os.path.exists(pid_file):
            try:
                with open(pid_file, 'r') as f:
                    doc_pid = int(f.read().strip())
                
                if psutil.pid_exists(doc_pid):
                    doc_process = psutil.Process(doc_pid)
                    if doc_process.status() != psutil.STATUS_ZOMBIE:
                        status["document_service"] = "running"
            except (FileNotFoundError, ValueError, psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logger.error(f"检查文档服务状态时出错: {str(e)}")
        
        return status
    except Exception as e:
        logger.error(f"检查服务状态时出错: {str(e)}")
        return {
            "api_service": "error",
            "ollama_service": "error",
            "document_service": "error"
        }

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html") as f:
        return f.read()

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        logger.info(f"接收到文件上传请求: {file.filename}")
        
        # 确保目录存在
        os.makedirs("input_docs", exist_ok=True)
        
        # 生成唯一的文件名
        base_name, ext = os.path.splitext(file.filename)
        counter = 1
        new_filename = file.filename
        while os.path.exists(os.path.join("input_docs", new_filename)):
            new_filename = f"{base_name}_{counter}{ext}"
            counter += 1
            
        logger.info(f"生成新文件名: {new_filename}")
        
        content = await file.read()
        logger.info(f"文件大小: {len(content)} 字节")
        
        # 检测文件编码
        encoding = get_file_encoding(content)
        logger.info(f"检测到文件编码: {encoding}")
        
        if not encoding:
            logger.error("无法检测文件编码")
            raise HTTPException(status_code=400, detail="无法检测文件编码")
            
        # 检测文件内容是否包含泰语
        text_content = content.decode(encoding)
        logger.info(f"文件内容长度: {len(text_content)} 字符")
        
        if not contains_thai_text(text_content):
            logger.error("文件不包含泰语文本")
            raise HTTPException(status_code=400, detail="文件不包含泰语文本")
        
        # 保存文件到 input_docs 目录
        filename = os.path.join("input_docs", new_filename)
        logger.info(f"保存文件到: {filename}")
        
        async with aiofiles.open(filename, 'wb') as f:
            await f.write(content)
            
        logger.info("文件上传成功")
        return JSONResponse({
            "success": True,
            "message": "文件上传成功",
            "filename": new_filename,
            "originalFilename": file.filename
        })
        
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return JSONResponse({
            "success": False,
            "message": str(e)
        }, status_code=400)

@app.get("/api/files")
async def list_files():
    try:
        # 获取输入文档列表
        input_files = []
        if os.path.exists("input_docs"):
            input_files = [f for f in os.listdir("input_docs") if os.path.isfile(os.path.join("input_docs", f))]
            
        # 获取翻译后的文档列表
        translated_files = []
        if os.path.exists("output_docs"):
            translated_files = [f for f in os.listdir("output_docs") if os.path.isfile(os.path.join("output_docs", f))]
            
        # 添加响应头以禁用缓存
        response = JSONResponse({
            "files": {
                "input": input_files,
                "translated": translated_files
            }
        })
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
        
    except Exception as e:
        logger.error(f"获取文件列表失败: {str(e)}")
        return JSONResponse({
            "error": str(e)
        }, status_code=500)

@app.get("/api/content")
async def get_file_content(file: str):
    try:
        logger.info(f"请求文件内容: {file}")
        if not os.path.exists(file):
            logger.error(f"文件不存在: {file}")
            raise HTTPException(status_code=404, detail="文件不存在")
            
        async with aiofiles.open(file, 'r') as f:
            content = await f.read()
            return PlainTextResponse(content)
            
    except Exception as e:
        logger.error(f"读取文件内容失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/translate", response_class=PlainTextResponse)
async def translate(text: str):
    try:
        logger.info(f"收到翻译请求，文本: {text}")
        
        # 检查 Ollama 服务是否可用
        try:
            health_check = requests.get("http://localhost:11434/api/tags")
            if health_check.status_code != 200:
                logger.error("Ollama 服务未响应")
                raise HTTPException(status_code=503, detail="Ollama 服务未启动或无法访问")
        except requests.exceptions.ConnectionError:
            logger.error("无法连接到 Ollama 服务")
            raise HTTPException(status_code=503, detail="无法连接到 Ollama 服务，请确保 Ollama 已启动")

        # 调用 Ollama API 进行翻译
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5",
                "prompt": f"将以下泰语翻译成中文，只返回中文翻译结果，不要解释，不要英文: {text}",
                "stream": False,
                "temperature": 0.1,  # 降低随机性，使输出更确定
                "top_p": 0.9,        # 控制采样范围
                "num_predict": 2000   # 增加生成长度限制，确保长文档能完整翻译
            }
        )
        
        logger.info(f"Ollama 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"翻译结果: {result}")
            # 提取翻译结果，去掉所有额外内容
            translation = result["response"].strip()
            
            # 去掉括号内的解释
            translation = re.sub(r'\([^)]*\)', '', translation)
            
            # 去掉包含 "Translation:", "=", "Or,", "would be:", "Literally:" 的部分
            markers = ["Translation:", "=", "Or,", "would be:", "Literally:"]
            for marker in markers:
                if marker in translation:
                    translation = translation.split(marker)[0]
            
            # 去掉包含英文的行
            translation = '\n'.join(line for line in translation.split('\n') 
                                 if not re.search(r'[a-zA-Z]', line))
            
            return translation.strip()
        else:
            error_msg = f"Ollama 服务返回错误: {response.text}"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
            
    except Exception as e:
        error_msg = f"翻译服务出错: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/api/history")
async def get_translation_history():
    try:
        cache_file = ".translation_cache/translation_cache.json"
        if not os.path.exists(cache_file):
            return JSONResponse({"history": []})
            
        async with aiofiles.open(cache_file, 'r') as f:
            content = await f.read()
            cache = json.loads(content)
            
        # 转换缓存数据为历史记录格式
        history = []
        for key, data in cache.items():
            # 检查是否是文件记录
            if isinstance(data, dict) and "translations" in data:
                for trans in data["translations"]:
                    history.append({
                        "filename": key,
                        "timestamp": trans.get("timestamp", ""),
                        "thai_text": trans.get("source", ""),
                        "chinese_text": trans.get("target", "")
                    })
            
        # 按时间戳倒序排序
        history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return JSONResponse({"history": history})
    except Exception as e:
        logger.error(f"获取翻译历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history/{filename}")
async def get_translation_record(filename: str):
    try:
        cache_file = ".translation_cache/translation_cache.json"
        if not os.path.exists(cache_file):
            raise HTTPException(status_code=404, detail="翻译记录不存在")
            
        async with aiofiles.open(cache_file, 'r') as f:
            content = await f.read()
            cache = json.loads(content)
            
        if filename not in cache:
            raise HTTPException(status_code=404, detail="该文件的翻译记录不存在")
            
        file_data = cache[filename]
        if not isinstance(file_data, dict) or "translations" not in file_data:
            raise HTTPException(status_code=404, detail="该文件的翻译记录格式不正确")
            
        # 获取最新的翻译记录
        translations = file_data["translations"]
        if not translations:
            raise HTTPException(status_code=404, detail="该文件没有翻译记录")
            
        latest_translation = translations[-1]  # 最新的翻译记录
        return JSONResponse({
            "thai_text": latest_translation.get("source", ""),
            "chinese_text": latest_translation.get("target", ""),
            "timestamp": latest_translation.get("timestamp", "")
        })
    except Exception as e:
        logger.error(f"获取翻译记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info("启动翻译服务...")
    uvicorn.run(app, host="0.0.0.0", port=3333)
