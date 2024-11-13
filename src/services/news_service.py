from typing import Optional, List
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from services.qq_service import QQService
from services.baidu_translate_service import TranslateService
from utils.config import Config
from utils.logger import Logger

class NewsService:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.qq_service = QQService()
        self.translate = TranslateService()
        
    def get_cs2_news(self):
        """获取CS2更新新闻"""
        try:
            # 参考原代码:
            # startLine: 50
            
            # endLine: 70
            
            url = "https://blog.counter-strike.net/index.php/category/updates/feed/"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "xml")
            item = soup.find("item")
            
            if not item:
                return
                
            title = item.title.text
            link = item.link.text
            description = item.description.text.replace("<br>", "\n")
            date = item.pubDate.text
            
            # 翻译内容
            title_cn = self.translate.translate(title)
            desc_cn = self.translate.translate(description)
            
            text = f"{title_cn}:\n{desc_cn}\n{link}"
            
            # 发送到配置的群
            groups = self.config.news["gid"]["cs2"].split(",")
            for gid in groups:
                self.qq_service.send_message(gid, text)
                time.sleep(3)
                
            return text
            
        except Exception as e:
            self.logger.error(f"Error getting CS2 news: {e}")
            return None
            
    def get_gpt_news(self):
        """获取GPT更新新闻"""
        try:
            # 参考原代码:
            # startLine: 73
            # endLine: 96
            
            url = "https://help.openai.com/en/articles/6825453-chatgpt-release-notes"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 获取最新更新内容
            latest_update = soup.find("div", class_="release-notes")
            if not latest_update:
                return
                
            content = latest_update.text.strip()
            content_cn = self.translate.translate(content)
            
            text = f"ChatGPT更新:\n{content_cn}\n{url}"
            
            # 发送到配置的群
            groups = self.config.news["gid"]["gpt"].split(",")
            for gid in groups:
                self.qq_service.send_message(gid, text)
                time.sleep(3)
                
            return text
            
        except Exception as e:
            self.logger.error(f"Error getting GPT news: {e}")
            return None