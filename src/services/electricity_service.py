import requests
from typing import Optional, Dict, Any
from utils.config import Config
from utils.logger import Logger

class ElectricityService:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.api_url = self.config.electricity['api_url']
        
    def query_electricity(self, room_id: str) -> Optional[Dict[str, Any]]:
        """查询电费"""
        try:
            params = {
                'room_id': room_id,
                'api_key': self.config.electricity['api_key']
            }
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            result = response.json()
            
            if result['code'] == 200:
                return {
                    'balance': result['data']['balance'],
                    'last_update': result['data']['last_update'],
                    'usage_today': result['data']['usage_today']
                }
            return None
            
        except Exception as e:
            self.logger.error(f"Error querying electricity: {e}")
            return None