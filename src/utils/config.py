import yaml
import os
from typing import Dict, Any
from pathlib import Path
from ruamel.yaml import YAML

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
                
        # 验证endpoints配置
        if 'endpoints' not in self.config_data['openai']:
            raise ValueError("openai配置缺少endpoints字段")
        
        endpoints = self.config_data['openai']['endpoints']
        if not isinstance(endpoints, list) or len(endpoints) == 0:
            raise ValueError("endpoints必须是非空列表")
        
        for endpoint in endpoints:
            if not all(k in endpoint for k in ['url', 'api_key', 'priority']):
                raise ValueError("每个endpoint配置必须包含url、api_key和priority字段")
                
        return True
    
    def update_bot_info(self, uid: str, name: str):
        """更新机器人信息到配置文件"""
        try:
            self.config_data['qq_bot']['bot_uid'] = str(uid)
            self.config_data['qq_bot']['bot_name'] = name
            
            root_dir = Path(__file__).parent.parent.parent
            config_path = root_dir / 'config' / 'config.yaml'
            
            # 读取原始文件内容以保留注释
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 使用ruamel.yaml替代pyyaml以保留注释
            yaml = YAML()
            yaml.preserve_quotes = True
            yaml.indent(mapping=2, sequence=4, offset=2)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f)
                
        except Exception as e:
            error_msg = str(e).encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
            raise Exception(f"更新配置文件失败: {error_msg}")