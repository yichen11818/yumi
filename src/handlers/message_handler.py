import random
from typing import Dict, Any, List, Optional
import re
from services.qq_service import QQService
from services.chat_service import ChatService
from services.image_service import ImageService
from utils.config import Config
from utils.logger import Logger
from handlers.command_handler import CommandHandler
from services.verification_service import VerificationService

class MessageHandler:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.qq_service = QQService()
        self.chat_service = ChatService()
        self.command_handler = CommandHandler()
        self.verification_service = VerificationService()
        
    def handle_message(self, data: Dict[str, Any]):
        """处理消息的主入口"""
        try:
            message_type = data.get("message_type")
            if message_type == "guild":
                return self._handle_guild_message(data)
                
            sender = data.get("sender", {})
            uid = sender.get("user_id")
            gid = data.get("group_id")
            message = data.get("message", [])
            
            # 记录消息
            self.logger.info(f"Received message from {uid} in group {gid}: {message}")
            
            # 处理优先级:
            # 1. 回复消息处理
            if self._is_reply_message(message):
                if self._handle_reply_message(message, gid, uid):
                    return
            
            # 2. 验证答案检查
            if gid and self._check_verification_answer(gid, uid, message):
                return
            
            # 3. 命令处理
            if self.command_handler.handle_command(self._extract_text(message), data):
                return
            
            # 4. 检查是否在验证中
            if gid and self.verification_service.is_pending_verification(gid, uid):
                # 如果用户在验证中,不处理其他消息
                return
            
            # 5. 最后才是GPT回复
            if (self._is_at_bot(message) or 
                "yumi" in self._extract_text(message).lower() or 
                gid is None):
                self._handle_chat_message(gid, uid, message)
                
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            error_msg = [self.qq_service.text(f"处理消息时发生错误: {str(e)}")]
            self.qq_service.send_message(gid, error_msg, uid)
            
    def _handle_chat_message(self, gid: Optional[int], uid: int, message: List[Dict[str, Any]]):
        """处理聊天消息"""
        # 提取纯文本内容
        clean_message = self._extract_text(message)
        session_id = f"G{gid}" if gid else f"P{uid}"
        
        # 获取回复
        reply = self.chat_service.chat(session_id, clean_message)
        
        # 构造回复消息
        reply_msg = [self.qq_service.text(reply)]
        self.qq_service.send_message(gid, reply_msg, uid)
        
    def _extract_text(self, message: List[Dict[str, Any]]) -> str:
        """从消息中提取纯文本内容"""
        text_parts = []
        for msg in message:
            if msg["type"] == "text":
                text_parts.append(msg["data"]["text"])
        return " ".join(text_parts).strip()
        
    def _is_at_bot(self, message: List[Dict[str, Any]]) -> bool:
        """检查消息是否@了机器人"""
        bot_qq = str(self.config.qq_bot["bot_uid"])
        for msg in message:
            if msg["type"] == "at" and msg["data"]["qq"] == bot_qq:
                return True
        return False
        
    def _handle_guild_message(self, data: Dict[str, Any]):
        """处理频道消息"""
        try:
            guild_id = data.get("guild_id")
            channel_id = data.get("channel_id")
            sender = data.get("sender", {})
            uid = sender.get("user_id")
            message = data.get("message", [])
            
            self.logger.info(
                f"Received guild message from {uid} in guild {guild_id} "
                f"channel {channel_id}: {message}"
            )
            
            # 处理频道消息的逻辑...
            
        except Exception as e:
            self.logger.error(f"Error handling guild message: {e}")

    def _is_reply_message(self, message: List[Dict[str, Any]]) -> bool:
        """检查是否是回复消息"""
        for msg in message:
            if msg["type"] == "reply":
                return True
        return False

    def _handle_reply_message(self, message: List[Dict[str, Any]], gid: Optional[int], uid: int) -> bool:
        """处理回复消息"""
        try:
            # 检查是否是管理员
            if str(uid) != self.config.qq_bot['admin_qq']:
                return False

            # 获取回复的消息ID和内容
            reply_id = None
            command = None
            
            for msg in message:
                if msg["type"] == "reply":
                    reply_id = int(msg["data"]["id"])
                elif msg["type"] == "text":
                    command = msg["data"]["text"].strip()

            if not (reply_id and command):
                return False

            # 检查命令是否是"撤回"
            if command == "撤回":
                if self.qq_service.delete_msg(reply_id):
                    success_msg = [self.qq_service.text("已撤回该消息")]
                    self.qq_service.send_message(gid, success_msg, uid)
                else:
                    error_msg = [self.qq_service.text("撤回消息失败")]
                    self.qq_service.send_message(gid, error_msg, uid)
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error handling reply message: {e}")
            return False

    def _check_verification_answer(self, gid: int, uid: int, message: List[Dict[str, Any]]) -> bool:
        """检查是否是验证答案"""
        try:
            text = self._extract_text(message)
            if not text.isdigit():
                return False
                
            answer = int(text)
            if self.verification_service.check_answer(gid, uid, answer):
                success_msg = [self.qq_service.text("验证通过,欢迎加入!")]
                self.qq_service.send_message(gid, success_msg)
                return True
                
            # 验证失败,踢出群聊
            self.qq_service.set_group_kick(gid, uid, "验证失败")
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking verification answer: {e}")
            return False