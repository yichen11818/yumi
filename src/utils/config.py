import yaml
import os
from typing import Dict, Any
from pathlib import Path

class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'config_data'):
            try:
                root_dir = Path(__file__).parent.parent.parent
                config_path = root_dir / 'config' / 'config.yaml'
                
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config_data = yaml.safe_load(f)
                self.validate_config()
            except Exception as e:
                error_msg = str(e).encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
                raise Exception(f"配置文件加载失败: {error_msg}")
        

    @property
    def qq_bot(self) -> Dict[str, Any]:
        return self.config_data['qq_bot']
        
    @property
    def openai(self) -> Dict[str, Any]:
        return self.config_data['openai']
    
    @property
    def chatgpt(self) -> Dict[str, Any]:
        return self.config_data['chatgpt']
        
    @property
    def replicate(self) -> Dict[str, Any]:
        return self.config_data['replicate']
        
    @property
    def baidu(self) -> Dict[str, Any]:
        return self.config_data['baidu']
        
    @property
    def baidu_vision(self) -> Dict[str, Any]:
        return self.config_data['baidu_vision']
        
    @property
    def electricity(self) -> Dict[str, Any]:
        return self.config_data['electricity']
        
    @property
    def news(self) -> Dict[str, Any]:
        return self.config_data['news']
        
    @property
    def database(self) -> Dict[str, Any]:
        return self.config_data['database']
        
    @property
    def google(self) -> Dict[str, Any]:
        return self.config_data['google']
    
    def validate_config(self):
        """验证配置文件的完整性"""
        required_sections = [
            'qq_bot',
            'openai',
            'chatgpt',
            'baidu',
            'replicate',
            'electricity',
            'news',
            'database',
            'google'
        ]
        
        for section in required_sections:
            if section not in self.config_data:
                raise ValueError(f"配置文件缺少必要的配置项: {section}")
                
        # 验证 qq_bot 部分的必要字段
        required_qq_bot_fields = [
            'cqhttp_url',
            'bot_uid',
            'admin_qq',
            'host',
            'port'
        ]
        
        for field in required_qq_bot_fields:
            if field not in self.config_data['qq_bot']:
                raise ValueError(f"qq_bot 配置缺少必要字段: {field}")
                
        return True