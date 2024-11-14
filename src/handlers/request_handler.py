from typing import Optional, Dict, Any
from utils.config import Config
from utils.logger import Logger
from services.qq_service import QQService

class RequestHandler:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.qq_service = QQService()
        
    async def handle(self, data: Dict[str, Any]) -> bool:
        """处理请求"""
        try:
            request_type = data.get('request_type')
            
            if request_type == 'friend':
                return await self._handle_friend_request(data)
            elif request_type == 'group':
                return await self._handle_group_request(data)
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling request: {e}")
            return False
            
    async def _handle_friend_request(self, data: Dict[str, Any]) -> bool:
        """处理好友请求"""
        try:
            flag = data.get("flag")
            user_id = data.get("user_id")
            comment = data.get("comment", "")
            
            # 记录请求日志
            self.logger.info(f"Friend request from {user_id}: {comment}")
            
            # 如果开启自动同意
            if self.config.qq_bot.get("auto_confirm", False):
                # 调用API同意好友请求
                url = f"{self.config.qq_bot['cqhttp_url']}/set_friend_add_request"
                data = {
                    "flag": flag,
                    "approve": True,
                    "remark": ""  # 可以根据需要设置备注
                }
                response = self.qq_service.session.post(url, json=data)
                response.raise_for_status()
                result = response.json()
                
                if result.get("status") == "ok":
                    self.logger.info(f"已自动同意好友请求: {user_id}")
                    return True
                else:
                    self.logger.error(f"同意好友请求失败: {result}")
                    return False
                
            # 否则转发给管理员
            admin_msg = (
                f"收到好友请求:\n"
                f"QQ: {user_id}\n"
                f"验证信息: {comment}"
            )
            self.qq_service.send_message(
                None, 
                admin_msg, 
                self.config.qq_bot["admin_qq"]
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Error handling friend request: {e}")
            return False
            
    async def _handle_group_request(self, data: Dict[str, Any]) -> bool:
        """处理群聊请求"""
        try:
            flag = data.get("flag")
            sub_type = data.get("sub_type")
            group_id = data.get("group_id")
            user_id = data.get("user_id")
            comment = data.get("comment", "")
            
            # 记录请求日志
            self.logger.info(f"Group {sub_type} request from {user_id} for group {group_id}: {comment}")
            
            if sub_type == "add":
                # 处理加群请求
                return await self._handle_group_add_request(flag, group_id, user_id, comment)
            elif sub_type == "invite":
                # 处理群邀请
                return await self._handle_group_invite_request(flag, group_id, user_id)
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling group request: {e}")
            return False
            
    async def _approve_friend_request(self, flag: str, approve: bool = True) -> bool:
        """处理好友请求"""
        try:
            url = f"{self.config.qq_bot['cqhttp_url']}/set_friend_add_request"
            data = {
                "flag": flag,
                "approve": approve
            }
            response = self.qq_service.session.post(url, json=data)
            response.raise_for_status()
            return response.json()["status"] == "ok"
            
        except Exception as e:
            self.logger.error(f"Error approving friend request: {e}")
            return False
            
    async def _handle_group_add_request(
        self, 
        flag: str, 
        group_id: int, 
        user_id: int, 
        comment: str
    ) -> bool:
        """处理加群请求"""
        try:
            # 如果开启自动同意
            if self.config.qq_bot.get("auto_confirm", False):
                return await self._approve_group_request(flag)
                
            # 否则转发给管理员
            admin_msg = (
                f"收到加群请求:\n"
                f"群号: {group_id}\n"
                f"QQ: {user_id}\n"
                f"验证信息: {comment}"
            )
            self.qq_service.send_message(
                None, 
                admin_msg, 
                self.config.qq_bot["admin_qq"]
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Error handling group add request: {e}")
            return False
            
    async def _handle_group_invite_request(
        self, 
        flag: str, 
        group_id: int, 
        user_id: int
    ) -> bool:
        """处理群邀请请求"""
        try:
            # 如果是管理员邀请,自动同意
            if str(user_id) == str(self.config.qq_bot["admin_qq"]):
                return await self._approve_group_request(flag)
                
            # 否则转发给管理员
            admin_msg = (
                f"收到群邀请:\n"
                f"群号: {group_id}\n"
                f"邀请人: {user_id}"
            )
            self.qq_service.send_message(
                None, 
                admin_msg, 
                self.config.qq_bot["admin_qq"]
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Error handling group invite request: {e}")
            return False
            
    async def _approve_group_request(self, flag: str, approve: bool = True) -> bool:
        """处理群请求"""
        try:
            url = f"{self.config.qq_bot['cqhttp_url']}/set_group_add_request"
            data = {
                "flag": flag,
                "approve": approve
            }
            response = self.qq_service.session.post(url, json=data)
            response.raise_for_status()
            return response.json()["status"] == "ok"
            
        except Exception as e:
            self.logger.error(f"Error approving group request: {e}")
            return False