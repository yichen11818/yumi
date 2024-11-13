import requests
from typing import Optional, Dict, Any, List, Union
from utils.config import Config
from utils.logger import Logger
import json

class QQService:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.base_url = self.config.qq_bot['cqhttp_url']
        self.session = requests.Session()
    
    def at(self, qq: Union[int, str]) -> Dict[str, Any]:
        """生成at消息"""
        return {
            "type": "at",
            "data": {
                "qq": str(qq)
            }
        }
        
    def text(self, text: str) -> Dict[str, Any]:
        """生成文本消息"""
        return {
            "type": "text",
            "data": {
                "text": text
            }
        }
        
    def image(self, file: str) -> Dict[str, Any]:
        """生成图片消息"""
        return {
            "type": "image",
            "data": {
                "file": file
            }
        }
        
    def music(self, type: str, id: str) -> Dict[str, Any]:
        """生成音乐分享消息"""
        return {
            "type": "music",
            "data": {
                "type": type,
                "id": id
            }
        }
        
    def reply(self, id: int) -> Dict[str, Any]:
        """生成回复消息"""
        return {
            "type": "reply",
            "data": {
                "id": str(id)
            }
        }

    def build_message(self, elements: List[Dict[str, Any]]) -> str:
        """将消息元素列表转换为JSON字符串"""
        return json.dumps(elements)

    def send_message(
        self,
        gid: Optional[int] = None,
        message: Optional[Union[str, List[Dict[str, Any]]]] = None,
        uid: Optional[int] = None,
        at: bool = True
    ) -> bool:
        """发送消息到群或私聊"""
        try:
            if message is None:
                raise ValueError("Message cannot be None")

            # 如果message是字符串,转换为text消息元素
            if isinstance(message, str):
                message = [self.text(message)]
                
            # 如果需要at且在群聊中
            if gid is not None and at and uid:
                message.insert(0, self.at(uid))
                
            # 转换为JSON字符串
            message_str = self.build_message(message)
            
            if gid is not None:
                url = f"{self.base_url}/send_group_msg"
                data = {"group_id": gid, "message": message_str}
            else:
                url = f"{self.base_url}/send_private_msg"
                data = {"user_id": uid, "message": message_str}
                
            response = self.session.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result['status'] == 'ok':
                self.logger.info(f"Message sent successfully: {message_str[:100]}...")
                return True
            else:
                self.logger.error(f"Failed to send message: {result.get('wording', 'Unknown error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False
            
    def get_user_info(self, uid: int) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        try:
            response = self.session.post(
                f"{self.base_url}/get_stranger_info",
                params={"user_id": uid, "no_cache": False}
            )
            response.raise_for_status()
            result = response.json()
            
            if result['status'] == 'ok':
                return result['data']
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting user info: {e}")
            return None
        
    def face(self, face_id: int) -> Dict[str, Any]:
        """生成QQ表情消息"""
        return {
            "type": "face",
            "data": {
                "id": str(face_id)
            }
        }
        
    def dice(self) -> Dict[str, Any]:
        """生成骰子消息"""
        return {
            "type": "dice",
            "data": {}
        }
        
    def rps(self) -> Dict[str, Any]:
        """生成石头剪刀布消息"""
        return {
            "type": "rps",
            "data": {}
        }
        
    def contact(self, type: str, id: str) -> Dict[str, Any]:
        """生成推荐好友/群消息"""
        return {
            "type": "contact",
            "data": {
                "type": type,
                "id": id
            }
        }
        
    def custom_music(self, url: str, audio: str, title: str, 
                    image: Optional[str] = None, 
                    singer: Optional[str] = None) -> Dict[str, Any]:
        """生成自定义音乐消息"""
        data = {
            "type": "custom",
            "url": url,
            "audio": audio,
            "title": title
        }
        if image:
            data["image"] = image
        if singer:
            data["singer"] = singer
            
        return {
            "type": "music",
            "data": data
        }
        
    def forward(self, id: str) -> Dict[str, Any]:
        """生成合并转发消息"""
        return {
            "type": "forward",
            "data": {
                "id": id
            }
        }

    def delete_msg(self, message_id: int) -> bool:
        """撤回消息"""
        try:
            url = f"{self.base_url}/delete_msg"
            data = {"message_id": message_id}
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()["status"] == "ok"
        except Exception as e:
            self.logger.error(f"Error deleting message: {e}")
            return False