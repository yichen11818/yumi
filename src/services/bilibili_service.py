import re
import os
import json
import time
import requests
from io import BytesIO
from typing import Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont
import textwrap
from datetime import datetime
from utils.config import Config
from utils.logger import Logger
from services.asset_service import AssetService

class BilibiliService:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.asset_service = AssetService()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def extract_video_id(self, url: str) -> Optional[str]:
        """提取B站视频ID"""
        try:
            patterns = [
                r'b23\.tv/([A-Za-z0-9]+)',  # b23.tv短链接
                r'bilibili\.com/video/([A-Za-z0-9]+)',  # 普通视频链接
                r'BV([A-Za-z0-9]+)'  # BV号
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting video ID: {e}")
            return None
            
    def fetch_video_details(self, url: str) -> Optional[Dict[str, Any]]:
        """获取视频详情"""
        try:
            video_id = self.extract_video_id(url)
            if not video_id:
                return None
                
            # 处理b23.tv短链接
            if 'b23.tv' in url:
                response = requests.get(url, headers=self.headers, allow_redirects=True)
                url = response.url
                video_id = self.extract_video_id(url)
                
            api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={video_id}"
            response = requests.get(api_url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            if data['code'] != 0:
                return None
                
            video_data = data['data']
            
            # 格式化时间
            publish_time = datetime.fromtimestamp(video_data['pubdate'])
            formatted_time = publish_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # 格式化时长
            duration = video_data['duration']
            minutes = duration // 60
            seconds = duration % 60
            formatted_duration = f"{minutes:02d}:{seconds:02d}"
            
            return {
                'title': video_data['title'],
                'desc': video_data['desc'],
                'cover_url': video_data['pic'],
                'author': video_data['owner']['name'],
                'view_count': self._format_number(video_data['stat']['view']),
                'like_count': self._format_number(video_data['stat']['like']),
                'coin_count': self._format_number(video_data['stat']['coin']),
                'share_count': self._format_number(video_data['stat']['share']),
                'duration': formatted_duration,
                'publish_time': formatted_time
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching video details: {e}")
            return None
            
    def create_video_card(self, video_details: Dict[str, Any]) -> Optional[str]:
        """生成视频信息卡片图片"""
        try:
            # 获取字体路径
            font_path = self.asset_service.get_font_path('msyh.ttc')
            if not font_path:
                raise FileNotFoundError("Font file not found")
                
            # 创建图片
            width = 800
            height = 400
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            
            # 加载字体
            title_font = ImageFont.truetype(str(font_path), 24)
            text_font = ImageFont.truetype(str(font_path), 18)
            
            # 下载并添加封面图
            cover_response = requests.get(video_details['cover_url'])
            cover_img = Image.open(BytesIO(cover_response.content))
            cover_img = cover_img.resize((300, 200))
            img.paste(cover_img, (20, 20))
            
            # 绘制标题
            title_wrapped = textwrap.fill(video_details['title'], width=25)
            draw.text((340, 20), title_wrapped, font=title_font, fill='black')
            
            # 绘制作者信息
            draw.text((340, 100), f"UP主: {video_details['author']}", font=text_font, fill='black')
            
            # 绘制统计信息
            stats_text = (
                f"播放: {video_details['view_count']}\n"
                f"点赞: {video_details['like_count']}\n"
                f"投币: {video_details['coin_count']}\n"
                f"分享: {video_details['share_count']}\n"
                f"时长: {video_details['duration']}\n"
                f"发布时间: {video_details['publish_time']}"
            )
            draw.text((340, 140), stats_text, font=text_font, fill='black')
            
            # 绘制简介
            if video_details['desc']:
                desc_wrapped = textwrap.fill(video_details['desc'][:200], width=35)
                draw.text((20, 240), "简介:\n" + desc_wrapped, font=text_font, fill='black')
                
            # 创建临时文件路径并保存
            temp_path = self.asset_service.create_temp_file(
                f'video_card_{int(time.time())}.png'
            )
            img.save(str(temp_path))
            return str(temp_path)
            
        except Exception as e:
            self.logger.error(f"Error creating video card: {e}")
            return None
            
    def _format_number(self, num: int) -> str:
        """格式化数字"""
        if num >= 100000000:
            return f"{num/100000000:.1f}亿"
        elif num >= 10000:
            return f"{num/10000:.1f}万"
        return str(num)