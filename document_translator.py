import os
import time
import json
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
import logging
import chardet

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentTranslator:
    def __init__(self):
        self.input_dir = "input_docs"
        self.output_dir = "output_docs"
        self.cache_dir = ".translation_cache"
        self.cache_file = os.path.join(self.cache_dir, "translation_cache.json")
        self.setup_directories()
        self.load_cache()

    def setup_directories(self):
        """创建必要的目录"""
        for directory in [self.input_dir, self.output_dir, self.cache_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

    def load_cache(self):
        """加载翻译缓存"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
            else:
                self.cache = {}
        except Exception as e:
            logger.error(f"加载缓存失败: {e}")
            self.cache = {}

    def save_cache(self):
        """保存翻译缓存"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")

    def get_file_hash(self, filepath):
        """计算文件的MD5哈希值"""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception as e:
            logger.error(f"计算文件哈希值失败: {e}")
            return None

    def needs_translation(self, filepath):
        """检查文件是否需要翻译"""
        file_hash = self.get_file_hash(filepath)
        if not file_hash:
            return True

        filename = os.path.basename(filepath)
        cached_info = self.cache.get(filename, {})
        
        # 如果文件哈希值不同，或者输出文件不存在，则需要翻译
        if (cached_info.get('hash') != file_hash or 
            not os.path.exists(os.path.join(self.output_dir, f"translated_{filename}"))):
            return True
            
        return False

    def detect_encoding(self, filepath):
        """检测文件编码"""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
                result = chardet.detect(content)
                return result['encoding']
        except Exception as e:
            logger.error(f"检测文件编码失败: {e}")
            return 'utf-8'

    def translate_file(self, filepath):
        """翻译文件"""
        if not self.needs_translation(filepath):
            logger.info(f"文件 {filepath} 无需翻译，使用缓存版本")
            return

        try:
            filename = os.path.basename(filepath)
            encoding = self.detect_encoding(filepath)
            
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()

            # 调用翻译API
            response = requests.get(
                "http://localhost:3333/api/translate",
                params={"text": content}
            )
            
            if response.status_code == 200:
                translated_text = response.text
                output_path = os.path.join(self.output_dir, f"translated_{filename}")
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(translated_text)
                
                # 更新缓存
                self.cache[filename] = {
                    'hash': self.get_file_hash(filepath),
                    'last_translated': time.time()
                }
                self.save_cache()
                
                logger.info(f"成功翻译文件: {filename}")
            else:
                logger.error(f"翻译失败: {response.text}")
                
        except Exception as e:
            logger.error(f"翻译文件时出错: {e}")

    def process_existing_files(self):
        """处理已存在的文件"""
        for filename in os.listdir(self.input_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(self.input_dir, filename)
                self.translate_file(filepath)

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, translator):
        self.translator = translator

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.txt'):
            return
        logger.info(f"检测到新文件: {event.src_path}")
        self.translator.translate_file(event.src_path)

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith('.txt'):
            return
        logger.info(f"检测到文件修改: {event.src_path}")
        self.translator.translate_file(event.src_path)

def main():
    translator = DocumentTranslator()
    
    # 处理已存在的文件
    translator.process_existing_files()
    
    # 设置文件监控
    event_handler = FileChangeHandler(translator)
    observer = Observer()
    observer.schedule(event_handler, translator.input_dir, recursive=False)
    observer.start()
    
    logger.info("文档翻译服务已启动，正在监控 input_docs 目录...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("文档翻译服务已停止")
    
    observer.join()

if __name__ == "__main__":
    main()
