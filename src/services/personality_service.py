from typing import Dict, Any
from utils.config import Config
from utils.logger import Logger

class PersonalityService:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.personalities = {}
        
    def set_personality(self, session_id: str, personality: str):
        """设置会话人格"""
        try:
            self.personalities[session_id] = personality
            self.logger.info(f"Set personality for session {session_id}: {personality}")
        except Exception as e:
            self.logger.error(f"Error setting personality: {e}")
            
    def get_personality(self, session_id: str) -> str:
        """获取会话人格"""
        return self.personalities.get(session_id, self.config.chatgpt['preset'])
        
    def reset_personality(self, session_id: str):
        """重置会话人格"""
        try:
            if session_id in self.personalities:
                del self.personalities[session_id]
            self.logger.info(f"Reset personality for session {session_id}")
        except Exception as e:
            self.logger.error(f"Error resetting personality: {e}")