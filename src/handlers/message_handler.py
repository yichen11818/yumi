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
        
    async def handle(self, data: Dict[str, Any]):
        """处理消息"""
        message_type = data.get('message_type')
        
        if message_type == 'group':
            await self._handle_group_message(data)
        elif message_type == 'private':
            await self._handle_private_message(data)
            
    async def _handle_group_message(self, data: Dict[str, Any]):
        """处理群消息"""
        gid = data.get('group_id')
        uid = data.get('user_id')
        message = data.get('message')
        
        # 处理@消息
        if self._is_at_bot(message):
            await self._handle_chat_message(gid, uid, message)
            
    async def _handle_chat_message(self, gid: int, uid: int, message: List[Dict[str, Any]]):
        """处理聊天消息"""
        try:
            # 提取纯文本消息
            text = self._extract_text(message)
            if not text:
                return
                
            # 调用ChatGPT API
            response = await self.chat_service.chat(f"group_{gid}_{uid}", text)
            
            # 发送回复
            self.qq_service.send_message(gid, response, uid)
            
        except Exception as e:
            self.logger.error(f"Error handling chat message: {e}")
        
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

    async def _handle_private_message(self, data: Dict[str, Any]):
        """处理私聊消息"""
        uid = data.get('user_id')
        message = data.get('message')
        
        # 提取纯文本消息
        text = self._extract_text(message)
        if not text:
            return
        
        try:
            # 调用ChatGPT API
            response = await self.chat_service.chat(f"private_{uid}", text)
            
            # 发送回复
            self.qq_service.send_message(None, response, uid)
            
        except Exception as e:
            self.logger.error(f"Error handling private message: {e}")