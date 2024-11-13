from typing import Optional
import requests
import hashlib
import random
from utils.config import Config
from utils.logger import Logger

class TranslateService:
    def __init__(self):
        self.config = Config()
        self.logger = Logger() 
        
    def translate(self, text: str, from_lang: str = 'en', to_lang: str = 'zh') -> Optional[str]:
        """百度翻译API"""
        try:
            appid = self.config.baidu['appid']
            secret_key = self.config.baidu['secret_key']
            
            salt = random.randint(32768, 65536)
            sign = appid + text + str(salt) + secret_key
            sign = hashlib.md5(sign.encode()).hexdigest()
            
            url = 'https://api.fanyi.baidu.com/api/trans/vip/translate'
            params = {
                'q': text,
                'from': from_lang,
                'to': to_lang,
                'appid': appid,
                'salt': salt,
                'sign': sign
            }
            
            response = requests.get(url, params=params)
            result = response.json()
            
            if 'trans_result' in result:
                return result['trans_result'][0]['dst']
            return None
            
        except Exception as e:
            self.logger.error(f"Translation error: {e}")
            return None