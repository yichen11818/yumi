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
        self.current_key_index = 0
        self.current_url_index = 0
        self.client = self._create_client()
        self.sessions = {}
        
    def _create_client(self) -> OpenAI:
        """创建OpenAI客户端"""
        try:
            api_key = self._get_current_api_key()
            base_url = self._get_current_base_url()
            
            return OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=30.0
            )
        except Exception as e:
            self.logger.error(f"创建OpenAI客户端失败: {e}")
            return None
            
    def _get_current_base_url(self) -> str:
        """获取当前base_url"""
        base_urls = sorted(
            self.config.openai['base_urls'],
            key=lambda x: x['priority']
        )
        return base_urls[self.current_url_index]['url']
        
    def _switch_base_url(self) -> bool:
        """切换到下一个base_url"""
        base_urls = self.config.openai['base_urls']
        if self.current_url_index < len(base_urls) - 1:
            self.current_url_index += 1
            self.client = self._create_client()
            self.logger.info(f"切换到备用API地址: {self._get_current_base_url()}")
            return True
        return False
        
    def _handle_api_error(self, e: Exception) -> Optional[str]:
        """处理API错误"""
        error_msg = str(e)
        self.logger.error(f"API调用失败: {error_msg}")
        
        if "connect" in error_msg.lower() or "timeout" in error_msg.lower():
            if self._switch_base_url():
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