from typing import Dict, Any
from services.qq_service import QQService
from utils.config import Config
from utils.logger import Logger
import json
import random
from services.verification_service import VerificationService

class NoticeHandler:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.qq_service = QQService()
        self.verification_service = VerificationService()
        
    async def handle(self, data: Dict[str, Any]):
        """处理通知消息"""
        try:
            notice_type = data.get("notice_type")
            sub_type = data.get("sub_type", "")
            
            # 好友相关通知
            if notice_type == "friend_add":
                self._handle_friend_add(data)
            elif notice_type == "friend_recall":
                self._handle_friend_recall(data)
                
            # 群组相关通知
            elif notice_type == "group_admin":
                self._handle_group_admin(data)
            elif notice_type == "group_ban":
                self._handle_group_ban(data)
            elif notice_type == "group_card":
                self._handle_group_card(data)
            elif notice_type == "group_decrease":
                self._handle_group_decrease(data)
            elif notice_type == "group_increase":
                self._handle_group_increase(data)
            elif notice_type == "group_recall":
                self._handle_group_recall(data)
            elif notice_type == "group_upload":
                self._handle_group_upload(data)
            elif notice_type == "essence":
                self._handle_essence(data)
                
            # 其他通知
            elif notice_type == "notify":
                if sub_type == "poke":
                    self._handle_poke(data)
                elif sub_type == "input_status":
                    self._handle_input_status(data)
                elif sub_type == "profile_like":
                    self._handle_profile_like(data)
                    
        except Exception as e:
            self.logger.error(f"Error handling notice: {e}")

    def _handle_friend_add(self, data: Dict[str, Any]):
        """处理好友添加通知"""
        user_id = data.get("user_id")
        self.logger.info(f"New friend added: {user_id}")
        
    def _handle_friend_recall(self, data: Dict[str, Any]):
        """处理私聊消息撤回"""
        user_id = data.get("user_id")
        message_id = data.get("message_id")
        recalled_message = self.qq_service.get_msg(message_id)
        self.logger.info(f"Friend {user_id} recalled message: {recalled_message}")
        
    def _handle_group_admin(self, data: Dict[str, Any]):
        """处理群管理员变动"""
        sub_type = data.get("sub_type")
        group_id = data.get("group_id")
        user_id = data.get("user_id")
        
        action = "设置" if sub_type == "set" else "取消"
        message = [
            self.qq_service.text(f"{user_id} 被{action}为管理员")
        ]
        self.qq_service.send_message(group_id, message)
        
    def _handle_group_ban(self, data: Dict[str, Any]):
        """处理群禁言"""
        sub_type = data.get("sub_type")
        group_id = data.get("group_id")
        user_id = data.get("user_id")
        operator_id = data.get("operator_id")
        duration = data.get("duration")
        
        action = "禁言" if sub_type == "ban" else "解除禁言"
        if action == "禁言":
            message = [
                self.qq_service.text(
                    f"{operator_id} 对 {user_id} 进行{action} {duration}秒"
                )
            ]
        else:
            message = [
                self.qq_service.text(
                    f"{operator_id} 解除了 {user_id} 的禁言"
                )
            ]
        self.qq_service.send_message(group_id, message)

    def _handle_poke(self, data: Dict[str, Any]):
        """处理戳一戳"""
        target_id = data.get("target_id")
        user_id = data.get("user_id")
        group_id = data.get("group_id")
        
        if target_id == int(self.config.qq_bot['bot_uid']):
            message = [
                self.qq_service.text("戳我干嘛喵~"),
                self.qq_service.face(random.randint(1, 200))  # 随机表情
            ]
            self.qq_service.send_message(group_id, message, user_id, at=False)
            
    def _handle_group_recall(self, data: Dict[str, Any]):
        """处理群消息撤回"""
        operator_id = data.get("operator_id")
        group_id = data.get("group_id")
        user_id = data.get("user_id")
        message_id = data.get("message_id")
        
        operator_name = self.qq_service.get_user_info(operator_id)['nickname']
        user_name = self.qq_service.get_user_info(user_id)['nickname']
        recalled_message = self.qq_service.get_msg(message_id)
        
        message = [
            self.qq_service.text(
                f"{operator_name}撤回了{user_name}的消息:\n{recalled_message}"
            )
        ]
        self.qq_service.send_message(group_id, message, user_id, at=False)

    def _handle_group_increase(self, data: Dict[str, Any]):
        """处理群成员增加"""
        group_id = data.get("group_id")
        user_id = data.get("user_id")
        
        # 检查是否开启验证
        if self.verification_service.is_verification_enabled(group_id):
            question, _ = self.verification_service.add_verification(group_id, user_id)
            message = [
                self.qq_service.text(
                    f"欢迎新成员 {user_id}\n"
                    f"请在5分钟内回答问题:\n"
                    f"{question}"
                )
            ]
            self.qq_service.send_message(group_id, message)