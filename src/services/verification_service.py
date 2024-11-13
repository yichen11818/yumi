from typing import Dict, Tuple, Optional
import random
import time
from utils.config import Config
from utils.logger import Logger
from services.qq_service import QQService

class VerificationService:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.qq_service = QQService()
        # 存储群验证状态: {group_id: bool}
        self.verification_status = {}
        # 存储待验证用户: {group_id: {user_id: (answer, timestamp)}}
        self.pending_verifications = {}
        
    def enable_verification(self, group_id: int) -> bool:
        """开启群验证"""
        self.verification_status[group_id] = True
        return True
        
    def disable_verification(self, group_id: int) -> bool:
        """关闭群验证"""
        self.verification_status[group_id] = False
        if group_id in self.pending_verifications:
            del self.pending_verifications[group_id]
        return True
        
    def is_verification_enabled(self, group_id: int) -> bool:
        """检查群是否开启验证"""
        return self.verification_status.get(group_id, False)
        
    def generate_question(self) -> Tuple[str, int]:
        """生成随机计算题"""
        operators = ['+', '-', '*']
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        op = random.choice(operators)
        
        if op == '+':
            answer = a + b
        elif op == '-':
            answer = a - b
        else:
            answer = a * b
            
        question = f"{a} {op} {b} = ?"
        return question, answer
        
    def add_verification(self, group_id: int, user_id: int) -> Tuple[str, int]:
        """添加验证任务"""
        question, answer = self.generate_question()
        
        if group_id not in self.pending_verifications:
            self.pending_verifications[group_id] = {}
            
        self.pending_verifications[group_id][user_id] = (answer, time.time())
        return question, answer
        
    def check_answer(self, group_id: int, user_id: int, answer: int) -> bool:
        """检查答案"""
        if group_id not in self.pending_verifications:
            return False
            
        if user_id not in self.pending_verifications[group_id]:
            return False
            
        correct_answer, timestamp = self.pending_verifications[group_id][user_id]
        
        # 移除验证任务
        del self.pending_verifications[group_id][user_id]
        if not self.pending_verifications[group_id]:
            del self.pending_verifications[group_id]
            
        return answer == correct_answer
        
    def check_timeout(self) -> None:
        """检查超时的验证"""
        current_time = time.time()
        timeout_users = []
        
        for group_id in list(self.pending_verifications.keys()):
            for user_id, (_, timestamp) in list(self.pending_verifications[group_id].items()):
                if current_time - timestamp > 300:  # 5分钟超时
                    timeout_users.append((group_id, user_id))
                    del self.pending_verifications[group_id][user_id]
                    
            if not self.pending_verifications[group_id]:
                del self.pending_verifications[group_id]
                
        return timeout_users 
        
    def is_pending_verification(self, group_id: int, user_id: int) -> bool:
        """检查用户是否在验证中"""
        if group_id not in self.pending_verifications:
            return False
        return user_id in self.pending_verifications[group_id]