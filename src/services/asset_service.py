import os
from pathlib import Path
import time
from typing import Optional
from utils.config import Config
from utils.logger import Logger

class AssetService:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.base_path = Path(__file__).parent.parent / 'assets'
        self._init_directories()
        
    def _init_directories(self):
        """初始化资源目录"""
        try:
            # 创建必要的目录
            directories = [
                'fonts',
                'images/templates',
                'images/temp/generated',
                'images/temp/cache',
                'audio/temp'
            ]
            
            for directory in directories:
                dir_path = self.base_path / directory
                dir_path.mkdir(parents=True, exist_ok=True)
                
        except Exception as e:
            self.logger.error(f"Error initializing asset directories: {e}")
            
    def get_font_path(self, font_name: str) -> Optional[Path]:
        """获取字体文件路径"""
        try:
            font_path = self.base_path / 'fonts' / font_name
            return font_path if font_path.exists() else None
        except Exception as e:
            self.logger.error(f"Error getting font path: {e}")
            return None
            
    def get_template_path(self, template_name: str) -> Optional[Path]:
        """获取模板文件路径"""
        try:
            template_path = self.base_path / 'images' / 'templates' / template_name
            return template_path if template_path.exists() else None
        except Exception as e:
            self.logger.error(f"Error getting template path: {e}")
            return None
            
    def create_temp_file(self, filename: str, subdir: str = 'generated') -> Path:
        """创建临时文件路径"""
        try:
            temp_dir = self.base_path / 'images' / 'temp' / subdir
            temp_dir.mkdir(parents=True, exist_ok=True)
            return temp_dir / filename
        except Exception as e:
            self.logger.error(f"Error creating temp file: {e}")
            raise
            
    def clean_temp_files(self, max_age: int = 3600):
        """清理临时文件"""
        try:
            current_time = time.time()
            temp_dirs = [
                self.base_path / 'images' / 'temp' / 'generated',
                self.base_path / 'images' / 'temp' / 'cache',
                self.base_path / 'audio' / 'temp'
            ]
            
            for temp_dir in temp_dirs:
                for file_path in temp_dir.glob('*'):
                    if file_path.is_file():
                        file_age = current_time - file_path.stat().st_mtime
                        if file_age > max_age:
                            file_path.unlink()
                            
        except Exception as e:
            self.logger.error(f"Error cleaning temp files: {e}")