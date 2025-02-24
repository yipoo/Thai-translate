import os
import time
import requests
from pathlib import Path
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import chardet

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DocumentTranslator:
    def __init__(self, input_dir="input_docs", output_dir="output_docs"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.api_url = "http://localhost:3333"
        
        # 确保输入输出目录存在
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

    def detect_encoding(self, file_path):
        """检测文件编码"""
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            return result['encoding']

    def translate_text(self, text):
        """调用翻译API"""
        try:
            response = requests.get(f"{self.api_url}/?text={text}")
            if response.status_code == 200:
                return response.text
            else:
                logger.error(f"翻译失败: {response.text}")
                return None
        except Exception as e:
            logger.error(f"翻译请求出错: {str(e)}")
            return None

    def translate_file(self, input_file):
        """翻译单个文件"""
        try:
            # 检测文件编码
            encoding = self.detect_encoding(input_file)
            if not encoding:
                encoding = 'utf-8'

            # 读取文件内容
            with open(input_file, 'r', encoding=encoding) as f:
                content = f.read()

            # 按段落分割并翻译
            paragraphs = content.split('\n\n')
            translated_paragraphs = []

            for i, para in enumerate(paragraphs):
                if para.strip():
                    logger.info(f"正在翻译第 {i+1}/{len(paragraphs)} 段...")
                    translated = self.translate_text(para.strip())
                    if translated:
                        translated_paragraphs.append(translated)
                    # 添加延时避免请求过快
                    time.sleep(1)

            # 创建输出文件
            output_file = self.output_dir / f"translated_{input_file.name}"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(translated_paragraphs))

            logger.info(f"文件翻译完成: {output_file}")
            return True

        except Exception as e:
            logger.error(f"处理文件 {input_file} 时出错: {str(e)}")
            return False

    def process_directory(self):
        """处理输入目录中的所有文件"""
        for file_path in self.input_dir.glob('*.txt'):
            logger.info(f"开始处理文件: {file_path}")
            self.translate_file(file_path)

class FileHandler(FileSystemEventHandler):
    def __init__(self, translator):
        self.translator = translator

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.txt'):
            logger.info(f"检测到新文件: {event.src_path}")
            self.translator.translate_file(Path(event.src_path))

def main():
    translator = DocumentTranslator()
    
    # 处理现有文件
    translator.process_directory()
    
    # 设置文件监控
    event_handler = FileHandler(translator)
    observer = Observer()
    observer.schedule(event_handler, str(translator.input_dir), recursive=False)
    observer.start()
    
    logger.info(f"开始监控输入目录: {translator.input_dir}")
    logger.info("将泰语文本文件(.txt)放入输入目录即可自动翻译")
    logger.info("翻译结果将保存在输出目录中")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("停止监控")
    
    observer.join()

if __name__ == "__main__":
    main()
