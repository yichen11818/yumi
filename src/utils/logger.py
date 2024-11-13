import logging
import os
from datetime import datetime
import sys

class Logger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'logger'):
            # 创建logger
            self.logger = logging.getLogger('qq_bot')
            self.logger.setLevel(logging.INFO)
            
            # 创建logs目录
            if not os.path.exists('logs'):
                os.makedirs('logs')
            
            # 文件处理器
            file_handler = logging.FileHandler(
                f'logs/bot_{datetime.now().strftime("%Y%m%d")}.log',
                encoding='utf-8'
            )
            file_handler.setLevel(logging.INFO)
            
            # 控制台处理器
            console_handler = logging.StreamHandler(sys.stdout)  # 明确指定stdout
            console_handler.setLevel(logging.INFO)
            
            # 设置格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def info(self, message):
        """记录信息"""
        try:
            self.logger.info(message)
        except UnicodeEncodeError:
            # 如果出现编码错误，尝试编码转换
            encoded_message = message.encode('utf-8', errors='ignore').decode('utf-8')
            self.logger.info(encoded_message)
    
    def error(self, message):
        """记录错误"""
        try:
            self.logger.error(message)
        except UnicodeEncodeError:
            # 如果出现编码错误，尝试编码转换
            encoded_message = message.encode('utf-8', errors='ignore').decode('utf-8')
            self.logger.error(encoded_message)
    
    def warning(self, msg):
        """记录警告日志"""
        try:
            self.logger.warning(str(msg))  # 确保转换为字符串
        except Exception as e:
            print(f"日志记录失败: {e}")