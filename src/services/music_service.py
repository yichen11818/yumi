import requests
from typing import Optional, Dict, Any
from utils.config import Config
from utils.logger import Logger

class MusicService:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.api_url = "http://music.163.com/api/search/pc"
        
    def search_song(self, keyword: str) -> Optional[Dict[str, Any]]:
        """搜索歌曲"""
        try:
            params = {
                's': keyword,
                'offset': 0,
                'limit': 1,
                'type': 1,
            }
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            result = response.json()
            
            if result['code'] == 200 and result['result']['songCount'] > 0:
                song = result['result']['songs'][0]
                return {
                    'name': song['name'],
                    'artists': ', '.join(artist['name'] for artist in song['artists']),
                    'album': song['album']['name'],
                    'music_id': song['id'],
                }
            return None
            
        except Exception as e:
            self.logger.error(f"Error searching song: {e}")
            return None
            
    def get_song_url(self, music_id: int) -> Optional[str]:
        """获取歌曲URL"""
        try:
            url = f"http://music.163.com/song/media/outer/url?id={music_id}.mp3"
            return url
        except Exception as e:
            self.logger.error(f"Error getting song URL: {e}")
            return None 