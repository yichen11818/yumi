from typing import List, Dict, Any, Optional
import json, tiktoken
import requests
from bs4 import BeautifulSoup
from openai import AsyncOpenAI
from utils.config import Config
from utils.logger import Logger
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import concurrent.futures

class ChatService:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.client = AsyncOpenAI(
            api_key=self.config.openai['endpoints'][0]['api_key'],
            base_url=self.config.openai['endpoints'][0]['url']
        )
        
    async def chat(self, session_id: str, message: str) -> str:
        try:
            # 使用异步API调用
            response = await self.client.chat.completions.create(
                model=self.config.chatgpt['model'],
                messages=[{
                    "role": "user",
                    "content": message
                }]
            )
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = self._handle_api_error(e)
            if error_msg:
                return error_msg
            return f"对话失败: {str(e)}"

    def _handle_api_error(self, e: Exception) -> Optional[str]:
        """处理API错误"""
        try:
            if hasattr(e, 'response'):
                response = e.response
                status = response.status_code
                error_data = response.json()
                
                error_msg = f"API错误 {status}"
                if 'error' in error_data:
                    error_msg += f": {error_data['error'].get('message', '未知错误')}"
                    
                if status == 401:
                    error_msg = "API密钥无效"
                elif status == 429:
                    error_msg = "API调用次数超限"
                elif status == 500:
                    error_msg = "API服务器错误"
                elif status == 503:
                    error_msg = "API服务不可用"
                    
                self.logger.error(
                    f"\nAPI错误详情:"
                    f"\n- 状态码: {status}"
                    f"\n- 响应: {error_data}"
                )
                return error_msg
                
            return None
            
        except Exception as e:
            self.logger.error(f"处理API错误时发生异常: {e}")
            return None