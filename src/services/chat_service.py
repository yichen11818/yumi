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
        self.client = self._create_client()
        self.sessions = {}
        
        # 定义可用的函数
        self.available_functions = {
            "get_weather": self._get_weather,
            "search_music": self._search_music,
            "translate_text": self._translate_text,
            "generate_image": self._generate_image,
            "search_internet": self._search_internet,
            "search_google": self._search_google,
            "get_url_content": self._get_url_content
        }
        
        # 定义函数描述
        self.function_descriptions = [
            {
                "name": "search_music",
                "description": "搜索音乐",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "搜索关键词"
                        }
                    },
                    "required": ["keyword"]
                }
            },
            {
                "name": "search_internet",
                "description": "使用Serper API搜索互联网内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索查询内容"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "search_google",
                "description": "使用Google自定义搜索API搜索并总结内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_terms": {
                            "type": "string",
                            "description": "搜索关键词"
                        },
                        "count": {
                            "type": "integer",
                            "description": "每次搜索的结果数量",
                            "default": 10
                        },
                        "iterations": {
                            "type": "integer",
                            "description": "搜索迭代次数",
                            "default": 1
                        }
                    },
                    "required": ["search_terms"]
                }
            },
            {
                "name": "get_url_content",
                "description": "获取指定URL的网页内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "要获取内容的URL"
                        }
                    },
                    "required": ["url"]
                }
            }
        ]
    
    def _create_client(self) -> OpenAI:
        return OpenAI(
            api_key=self.config.openai['api_key'][self.current_key_index],
            base_url=self.config.openai.get('vip_base_url')
        )
        
    def chat(self, session_id: str, message: str) -> str:
        try:
            session = self.get_session(session_id)
            
            if message.strip() == "重置会话":
                self._reset_session(session)
                return "会话已重置"
                
            session['messages'].append({
                "role": "user",
                "content": message
            })
            
            response = self.client.chat.completions.create(
                model=self.config.chatgpt['model'],
                messages=session['messages'],
                functions=self.function_descriptions,
                function_call="auto"
            )
            
            response_message = response.choices[0].message
            
            # 处理函数调用
            if response_message.function_call:
                function_name = response_message.function_call.name
                function_args = json.loads(response_message.function_call.arguments)
                
                # 调用对应函数
                if function_name in self.available_functions:
                    function_response = self.available_functions[function_name](**function_args)
                    
                    # 将函数调用和结果添加到会话历史
                    session['messages'].append({
                        "role": "assistant",
                        "content": None,
                        "function_call": {
                            "name": function_name,
                            "arguments": response_message.function_call.arguments
                        }
                    })
                    
                    session['messages'].append({
                        "role": "function",
                        "name": function_name,
                        "content": json.dumps(function_response, ensure_ascii=False)
                    })
                    
                    # 让模型继续对话
                    second_response = self.client.chat.completions.create(
                        model=self.config.chatgpt['model'],
                        messages=session['messages']
                    )
                    
                    reply = second_response.choices[0].message.content
                else:
                    reply = "抱歉,该功能暂不可用"
            else:
                reply = response_message.content
                
            session['messages'].append({
                "role": "assistant",
                "content": reply
            })
            
            # 检查并清理过长的会话历史
            self._cleanup_session(session)
            
            return reply
            
        except Exception as e:
            self.logger.error(f"Chat error: {e}")
            return f"发生错误: {str(e)}"

    def get_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "messages": [
                    {"role": "system", "content": self.config.chatgpt['preset']}
                ]
            }
        return self.sessions[session_id]
        
    def _reset_session(self, session: Dict[str, Any]):
        """重置会话但保留系统预设"""
        system_message = session['messages'][0]
        session['messages'] = [system_message]
        
    def _cleanup_session(self, session: Dict[str, Any]):
        """清理过长的会话历史"""
        while self._count_tokens(session['messages']) > self.config.chatgpt['max_tokens']:
            # 保留系统消息和最后两轮对话
            if len(session['messages']) > 5:
                session['messages'].pop(1)
                
    def _count_tokens(self, messages: List[Dict[str, str]]) -> int:
        try:
            encoding = tiktoken.encoding_for_model(self.config.chatgpt['model'])
            num_tokens = 0
            for message in messages:
                num_tokens += 4
                for key, value in message.items():
                    num_tokens += len(encoding.encode(str(value)))
                    if key == "name":
                        num_tokens -= 1
            return num_tokens + 2
        except Exception as e:
            self.logger.error(f"Error counting tokens: {e}")
            return 0

    def _get_weather(self, city: str) -> Dict[str, Any]:
        """获取天气信息"""
        # 这里实现天气查询逻辑
        return {
            "city": city,
            "temperature": "25°C",
            "weather": "晴",
            "humidity": "65%"
        }
        
    def _search_music(self, keyword: str) -> Dict[str, Any]:
        """搜索音乐"""
        from services.music_service import MusicService
        music_service = MusicService()
        result = music_service.search_song(keyword)
        return result if result else {"error": "未找到相关音乐"}
        
    def _translate_text(self, text: str, target_lang: str) -> Dict[str, Any]:
        """翻译文本"""
        from services.baidu_translate_service import TranslateService
        translate_service = TranslateService()
        result = translate_service.translate(text, to_lang=target_lang)
        return {"translated_text": result} if result else {"error": "翻译失败"}
        
    def _generate_image(self, prompt: str) -> Dict[str, Any]:
        """生成图片"""
        from services.image_service import ImageService
        image_service = ImageService()
        image_url = image_service.generate_openai_image(prompt)
        return {"image_url": image_url} if image_url else {"error": "图片生成失败"}

    def _search_internet(self, query: str) -> Dict[str, Any]:
        """使用Serper API搜索互联网内容"""
        if not query or len(query.strip()) == 0:
            return {
                "status": "error",
                "message": "搜索查询不能为空"
            }
        try:
            result = self.search_internet({"q": query})
            return {
                "status": "success",
                "results": result
            }
        except Exception as e:
            self.logger.error(f"Search internet error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def _search_google(self, search_terms: str, count: int = 10, iterations: int = 1) -> Dict[str, Any]:
        """使用Google自定义搜索API搜索并总结内容"""
        if not search_terms or len(search_terms.strip()) == 0:
            return {
                "status": "error",
                "message": "搜索关键词不能为空"
            }
        if count < 1 or count > 50:
            count = 10
        if iterations < 1 or iterations > 5:
            iterations = 1
        
        try:
            all_summaries = []
            base_url = "https://www.googleapis.com/customsearch/v1?"
            api_key = self.config.google['api_key']
            cx_id = self.config.google['cx_id']

            for i in range(iterations):
                startIndex = i * count + 1
                search_url = self.build_search_url(
                    search_terms,
                    base_url=base_url,
                    count=count,
                    cx=cx_id,
                    key=api_key,
                    startIndex=startIndex
                )
                
                try:
                    response = requests.get(search_url)
                    if response.status_code == 200:
                        items = response.json().get('items', [])
                        
                        with ThreadPoolExecutor(max_workers=5) as executor:
                            future_to_item = {
                                executor.submit(
                                    self.get_summary, 
                                    item, 
                                    self.client, 
                                    search_terms
                                ): item for item in items
                            }
                            for future in as_completed(future_to_item):
                                try:
                                    summary = future.result(timeout=5)
                                    if summary:
                                        all_summaries.append("【搜索结果内容摘要】：\n" + summary)
                                except concurrent.futures.TimeoutError:
                                    self.logger.error("处理摘要任务超时")
                                except Exception as e:
                                    self.logger.error(f"在提取摘要过程中出现错误：{str(e)}")
                    else:
                        self.logger.error(f"Google搜索请求失败: {search_url}")
                        return {"error": "搜索请求失败"}
                except requests.RequestException as e:
                    self.logger.error(f"Google搜索请求失败: {e}")
                    return {"error": "搜索请求失败"}
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON解析失败: {e}")
                    return {"error": "返回数据格式错误"}

            return {
                "status": "success",
                "summaries": all_summaries if all_summaries else ["实时联网暂未获取到有效信息内容，请更换关键词或再次重试······"]
            }
        except Exception as e:
            self.logger.error(f"Google search error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def _get_url_content(self, url: str) -> Dict[str, Any]:
        """获取指定URL的网页内容"""
        if not self._validate_url(url):
            return {
                "status": "error",
                "message": "无效的URL格式"
            }
        try:
            content = self.get_url(url)
            if content:
                return {
                    "status": "success",
                    "content": content
                }
            else:
                return {
                    "status": "error",
                    "message": "无法获取URL内容"
                }
        except Exception as e:
            self.logger.error(f"Get URL content error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def process_content(self, content: str, model: OpenAI, search_terms: str) -> str:
        """处理和总结内容"""
        try:
            response = model.chat.completions.create(
                model=self.config.chatgpt['model'],
                messages=[
                    {"role": "system", "content": "请总结以下与搜索词相关的内容要点:"},
                    {"role": "user", "content": f"搜索词: {search_terms}\n内容: {content}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error processing content: {e}")
            return ""

    def _validate_url(self, url: str) -> bool:
        """验证URL是否有效"""
        try:
            result = urllib.parse.urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def search_internet(self, query: Dict[str, str]) -> Dict[str, Any]:
        """使用 Serper API 搜索互联网内容"""
        url = "https://google.serper.dev/search"
        
        headers = {
            'X-API-KEY': self.config.google['serper_api_key'],
            'Content-Type': 'application/json'
        }
        
        try:
            payload = json.dumps(query)
            res = requests.post(url, headers=headers, data=payload)
            if res.status_code == 200:
                try:
                    return res.json()
                except json.JSONDecodeError:
                    self.logger.error("响应不是有效的 JSON 格式")
                    return {"error": "响应不是有效的 JSON 格式"}
            else:
                error_msg = f"请求失败，状态码: {res.status_code}"
                self.logger.error(error_msg)
                return {"error": error_msg}
        except Exception as e:
            self.logger.error(f"Search internet error: {str(e)}")
            return {"error": str(e)}

    def get_url(self, url: str) -> Optional[List[str]]:
        """获取URL内容"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers, timeout=2)
            response.raise_for_status()
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            paragraphs = soup.find_all('p')
            return [p.get_text() for p in paragraphs]
        except Exception as e:
            self.logger.error(f"无法访问该URL: {url}, error: {str(e)}")
            return None

    def build_search_url(self, search_terms: str, **kwargs) -> str:
        """构建谷歌搜索URL"""
        params = {
            "q": search_terms,
            "num": kwargs.get("count"),
            "start": kwargs.get("startIndex"),
            "lr": kwargs.get("language"),
            "cx": kwargs.get("cx"),
            "sort": "date",
            "filter": 1,
            "hq": kwargs.get("hq"),
            "dateRestrict": kwargs.get("dateRestrict"),
            "key": kwargs.get("key"),
            "alt": "json"
        }
        params = {k: v for k, v in params.items() if v is not None}
        return kwargs.get("base_url") + urllib.parse.urlencode(params)

    def get_summary(self, item: Dict[str, Any], model: OpenAI, search_terms: str) -> Optional[str]:
        """获取内容摘要"""
        link_content = self.get_url(item["link"])
        if not link_content:
            self.logger.error(f"无法获取链接内容：{item['link']}")
            return None

        link_content_str = ' '.join(link_content)
        content_length = len(link_content_str)

        if content_length < 200:
            self.logger.info(f"链接内容低于200个字符：{item['link']}")
            return None
        elif content_length > 8000:
            self.logger.info(f"链接内容高于8000个字符，进行裁断：{item['link']}")
            start = (content_length - 8000) // 2
            end = start + 8000
            link_content = link_content[start:end]

        return self.process_content(str(link_content), model=model, search_terms=search_terms)

    def list_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        try:
            response = self.client.models.list()
            # 只返回 GPT 相关模型
            gpt_models = [
                model.id for model in response 
                if "gpt" in model.id.lower()
            ]
            return sorted(gpt_models)
        except Exception as e:
            self.logger.error(f"Error listing models: {e}")
            return []