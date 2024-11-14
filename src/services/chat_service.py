from typing import List, Dict, Any, Optional
import json, tiktoken
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from utils.config import Config
from utils.logger import Logger
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import concurrent.futures

class ChatService:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.current_endpoint_index = 0
        self.client = self._create_client()
        self.sessions = {}
        
    def _create_client(self) -> OpenAI:
        """创建OpenAI客户端"""
        try:
            endpoint = self._get_current_endpoint()
            return OpenAI(
                api_key=endpoint['api_key'],
                base_url=endpoint['url'],
                timeout=30.0
            )
        except Exception as e:
            self.logger.error(f"创建OpenAI客户端失败: {e}")
            return None
            
    def _get_current_endpoint(self) -> Dict[str, Any]:
        """获取当前endpoint配置"""
        endpoints = sorted(
            self.config.openai['endpoints'],
            key=lambda x: x['priority']
        )
        return endpoints[self.current_endpoint_index]
        
    def _switch_endpoint(self) -> bool:
        """切换到下一个endpoint"""
        endpoints = self.config.openai['endpoints']
        if self.current_endpoint_index < len(endpoints) - 1:
            self.current_endpoint_index += 1
            self.client = self._create_client()
            current = self._get_current_endpoint()
            self.logger.info(f"切换到备用API地址: {current['url']}")
            return True
        return False
        
    def _handle_api_error(self, e: Exception) -> Optional[str]:
        """处理API错误"""
        error_msg = str(e)
        self.logger.error(f"API调用失败: {error_msg}")
        
        if "connect" in error_msg.lower() or "timeout" in error_msg.lower():
            if self._switch_endpoint():
                return "API连接失败,已切换到备用地址,请重试"
            else:
                return "所有API地址均不可用,请稍后再试"
        return None

    async def chat(self, session_id: str, message: str) -> str:
        try:
            # 原有的chat逻辑
            response = await self.client.chat.completions.create(
                model=self.config.chatgpt['model'],
                messages=[{"role": "user", "content": message}]
            )
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = self._handle_api_error(e)
            if error_msg:
                return error_msg
            return f"对话失败: {str(e)}"