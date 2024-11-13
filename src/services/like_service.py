import random
import time
from typing import Optional, List
from utils.config import Config
from utils.logger import Logger
from services.qq_service import QQService

class LikeService:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.qq_service = QQService()
        
    def send_like(self, uid: int, times: int = 10) -> bool:
        """发送点赞"""
        try:
            url = f"{self.config.qq_bot['cqhttp_url']}/send_like"
            data = {
                "user_id": uid,
                "times": times
            }
            response = self.qq_service.session.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result['status'] == 'ok':
                self.logger.info(f"Successfully sent {times} likes to {uid}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error sending likes: {e}")
            return False
            
    def batch_send_likes(self, uids: List[int], times: int = 10) -> dict:
        """批量发送点赞"""
        results = {}
        for uid in uids:
            success = self.send_like(uid, times)
            results[uid] = success
            if success:
                # 随机延迟1-3秒,避免频率过快
                time.sleep(random.uniform(1, 3))
        return results
        
    def get_like_limit(self, uid: int) -> Optional[int]:
        """获取剩余点赞次数"""
        try:
            url = f"{self.config.qq_bot['cqhttp_url']}/get_like_limit"
            params = {"user_id": uid}
            response = self.qq_service.session.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            
            if result['status'] == 'ok':
                return result['data']['limit']
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting like limit: {e}")
            return None