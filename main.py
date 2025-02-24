from fastapi import FastAPI, HTTPException
import requests
from fastapi.middleware.cors import CORSMiddleware
import logging
from fastapi.responses import PlainTextResponse
import re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=PlainTextResponse)
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
                "stream": False
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

if __name__ == "__main__":
    import uvicorn
    logger.info("启动翻译服务...")
    uvicorn.run(app, host="0.0.0.0", port=3333)
