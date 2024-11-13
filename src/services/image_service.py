from typing import Optional, List
import random
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
from utils.config import Config
from utils.logger import Logger

class ImageService:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.client = OpenAI(api_key=self.config.openai['api_key'][0])
        
    def generate_openai_image(self, prompt: str) -> Optional[str]:
        """使用OpenAI生成图片"""
        try:
            response = self.client.images.generate(
                prompt=prompt,
                n=1,
                size=self.config.openai['img_size']
            )
            return response.data[0].url
        except Exception as e:
            self.logger.error(f"Error generating OpenAI image: {e}")
            return None
            
    def get_random_images(self, keyword: str, count: int = 1) -> List[str]:
        """获取随机图片"""
        try:
            page = random.randint(1, 100)
            url = f"https://www.duitang.com/search/?kw={keyword}&type=feed&start={page*24}"
            
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            images = soup.find_all("div", class_="mbpho")
            
            image_urls = []
            for img in images:
                src = img.find("img").get("src")
                if src:
                    image_urls.append(src)
                    
            return random.sample(image_urls, min(count, len(image_urls)))
            
        except Exception as e:
            self.logger.error(f"Error getting random images: {e}")
            return []
            
    def get_qq_avatar(self, uid: int, size: int = 640) -> str:
        """获取QQ头像"""
        return f"https://q.qlogo.cn/g?b=qq&nk={uid}&s={size}"