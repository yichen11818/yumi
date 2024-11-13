from typing import Dict, Any, Optional
import re
import yaml
from services.bilibili_service import BilibiliService
from services.qq_service import QQService
from services.chat_service import ChatService
from services.image_service import ImageService
from services.feature_service import FeatureService
from services.like_service import LikeService
from services.music_service import MusicService
from services.stable_diffusion_service import StableDiffusionService
from services.electricity_service import ElectricityService
from services.personality_service import PersonalityService
from services.verification_service import VerificationService
from utils.config import Config
from utils.logger import Logger

class CommandHandler:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.qq_service = QQService()
        self.chat_service = ChatService()
        self.image_service = ImageService()
        self.feature_service = FeatureService()
        self.music_service = MusicService()
        self.stable_diffusion_service = StableDiffusionService()
        self.electricity_service = ElectricityService()
        self.personality_service = PersonalityService()
        self.like_service = LikeService()
        self.bilibili_service = BilibiliService()
        self.verification_service = VerificationService()

    def handle_command(self, command: str, data: Dict[str, Any]) -> bool:
        """处理命令"""
        try:
            gid = data.get("group_id")
            uid = data.get("sender", {}).get("user_id")
            
            # 图片生成命令
            if command.startswith(("生成图像", "直接生成图像")):
                return self._handle_image_generation(command, gid, uid)
                
            # 今日老婆命令
            elif "今日老婆" in command or "每日老婆" in command:
                return self._handle_daily_wife(gid, uid)
                
            # 翻译命令
            elif command.startswith("翻译"):
                return self._handle_translation(command, gid, uid)
                    
            # 点歌命令
            elif command.startswith("点歌"):
                return self._handle_music_request(command, gid, uid)
                
            # 图片识别命令
            elif command == "图片识别" and "image" in data['message']:
                return self._handle_image_recognition(data, gid, uid)
                
            # Stable Diffusion命令
            elif command.startswith("/sd"):
                return self._handle_stable_diffusion(command, gid, uid)
                
            # 电费查询命令
            elif command.startswith("电费查询"):
                return self._handle_electricity_query(command, gid, uid)
            
            # 切换模型命令
            elif command.startswith("切换模型"):
                return self._handle_model_switch(command, gid, uid)
                
            # 查看当前模型命令
            elif command.strip() == "当前模型":
                return self._show_current_model(gid, uid)

            # 查看支持模型命令
            elif command.strip() == "支持模型":
                return self._handle_list_models(gid, uid)
                
            # 点赞命令
            elif command.startswith("赞我"):
                return self._handle_like_command(command, gid, uid)
            
            # 批量点赞命令
            elif command.startswith("批量赞我"):
                return self._handle_batch_like_command(command, gid, uid)

            elif command.startswith("设置人格"):
                return self._handle_set_personality(command, gid, uid) 
                
            elif "b23.tv" in command or "bilibili.com" in command:
                return self._handle_bilibili_link(command, gid, uid)
            
            # 验证相关命令
            elif command == "开启入群验证":
                return self._handle_enable_verification(gid, uid)
            elif command == "关闭入群验证":
                return self._handle_disable_verification(gid, uid)
            elif command.startswith("开启") and command.endswith("入群验证"):
                return self._handle_enable_verification(gid, uid)
                
        except Exception as e:
            self.logger.error(f"Error handling command: {e}")
            return False
            
    def _handle_image_generation(self, command: str, gid: Optional[int], uid: int) -> bool:
        """处理图片生成命令"""
        try:
            prompt = command.replace("生成图像", "").replace("直接生成图像", "").strip()
            image_url = self.image_service.generate_openai_image(prompt)
            if image_url:
                message = [self.qq_service.image(image_url)]
                self.qq_service.send_message(gid, message, uid)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error generating image: {e}")
            return False
        
    def _handle_model_switch(self, command: str, gid: Optional[int], uid: int) -> bool:
        """处理模型切换命令"""
        try:
            # 检查是否是管理员
            if str(uid) != self.config.qq_bot['admin_qq']:
                self.qq_service.send_message(gid, "只有管理员才能切换模型", uid)
                return True
                
            model = command.replace("切换模型", "").strip()
            if not model:
                self.qq_service.send_message(gid, "请指定要切换的模型", uid)
                return True
                
            # 更新配置
            self.config.config_data['chatgpt']['model'] = model
            # 保存到文件
            with open('config/config.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(self.config.config_data, f, allow_unicode=True)
                
            self.qq_service.send_message(gid, f"已切换到模型: {model}", uid)
            return True
            
        except Exception as e:
            self.logger.error(f"Error switching model: {e}")
            return False
        
    def _handle_list_models(self, gid: Optional[int], uid: int) -> bool:
        """处理查询支持模型命令"""
        try:
            # 检查是否是管理员
            if str(uid) != self.config.qq_bot['admin_qq']:
                self.qq_service.send_message(gid, "只有管理员才能查询支持的模型", uid)
                return True
                
            models = self.chat_service.list_available_models()
            if models:
                message = "支持的模型列表:\n" + "\n".join(models)
                self.qq_service.send_message(gid, message, uid)
            else:
                self.qq_service.send_message(gid, "获取模型列表失败", uid)
            return True
            
        except Exception as e:
            self.logger.error(f"Error listing models: {e}")
            return False   
        
    def _show_current_model(self, gid: Optional[int], uid: int) -> bool:
        """显示当前使用的模型"""
        try:
            current_model = self.config.chatgpt['model']
            self.qq_service.send_message(gid, f"当前使用的模型是: {current_model}", uid)
            return True
        except Exception as e:
            self.logger.error(f"Error showing current model: {e}")
            return False    
        
    def _handle_daily_wife(self, gid: Optional[int], uid: int) -> bool:
        """处理今日老婆命令"""
        try:
            if not gid:
                return False
                
            attributes = self.feature_service.get_daily_wife(gid)
            if not attributes:
                return False
                
            wife_id = self.qq_service.get_random_member(gid)
            wife_name = self.qq_service.get_user_info(wife_id)["nickname"]
            
            # 构造文本消息
            text_message = [
                self.qq_service.text(
                    f"你的老婆:\n"
                    f"{wife_name}({wife_id})\n"
                    f"{attributes['age']}|{attributes['height']}|{attributes['weight']}\n"
                    f"{attributes['race']}|{attributes['cup']}\n"
                    f"{attributes['hobby']}|{attributes['personality']}\n"
                    f"{attributes['style']}"
                )
            ]
            self.qq_service.send_message(gid, text_message, uid)
            
            # 发送头像
            avatar_url = self.image_service.get_qq_avatar(wife_id)
            avatar_message = [self.qq_service.image(avatar_url)]
            self.qq_service.send_message(gid, avatar_message, uid)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error handling daily wife: {e}")
            return False
        
    def _handle_music_request(self, command: str, gid: Optional[int], uid: int) -> bool:
        """处理点歌命令"""
        try:
            keyword = command.replace("点歌", "").strip()
            song_info = self.music_service.search_song(keyword)
            if song_info:
                message = [self.qq_service.music("163", song_info['music_id'])]
                self.qq_service.send_message(gid, message, uid)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error handling music request: {e}")
            return False
        
    def _handle_image_recognition(self, data: Dict[str, Any], gid: Optional[int], uid: int) -> bool:
        """处理图片识别命令"""
        try:
            # 从消息中提取图片URL
            for msg in data['message']:
                if msg['type'] == 'image':
                    image_url = msg['data']['url']
                    result = self.image_recognition_service.recognize_image(image_url)
                    if result:
                        message = [
                            self.qq_service.text(
                                "识别结果:\n" + 
                                "\n".join([f"{item['keyword']} ({item['score']:.2f})" 
                                         for item in result[:5]])
                            )
                        ]
                        self.qq_service.send_message(gid, message, uid)
                        return True
            return False
        except Exception as e:
            self.logger.error(f"Error handling image recognition: {e}")
            return False
        
    def _handle_stable_diffusion(self, command: str, gid: Optional[int], uid: int) -> bool:
        """处理SD图片生成命令"""
        try:
            prompt = command.replace("/sd", "").strip()
            images = self.stable_diffusion_service.generate_image(prompt)
            if images:
                for image_url in images:
                    message = [self.qq_service.image(image_url)]
                    self.qq_service.send_message(gid, message, uid)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error handling stable diffusion: {e}")
            return False
        
    def _handle_electricity_query(self, command: str, gid: Optional[int], uid: int) -> bool:
        room_id = command.replace("电费查询", "").strip()
        result = self.electricity_service.query_electricity(room_id)
        if result:
            message = f"电费查询结果:\n余额: {result['balance']}元\n今日用电: {result['usage_today']}度\n最后更新: {result['last_update']}"
            self.qq_service.send_message(gid, message, uid)
            return True
        return False
    
    def _handle_like_command(self, command: str, gid: Optional[int], uid: int) -> bool:
        """处理点赞命令"""
        try:
            # 解析目标用户ID
            parts = command.split()
            if len(parts) < 2:
                self.qq_service.send_message(gid, "请指定要点赞的用户QQ号", uid)
                return True
                
            target_uid = int(parts[1])
            times = 10  # 默认点赞次数
            
            if len(parts) > 2:
                times = min(int(parts[2]), 20)  # 限制最大点赞次数
                
            success = self.like_service.send_like(target_uid, times)
            
            if success:
                self.qq_service.send_message(
                    gid,
                    f"已成功给{target_uid}点赞{times}次",
                    uid
                )
            else:
                self.qq_service.send_message(
                    gid,
                    f"给{target_uid}点赞失败",
                    uid
                )
            return True
            
        except ValueError:
            self.qq_service.send_message(gid, "QQ号格式错误", uid)
            return True
        except Exception as e:
            self.logger.error(f"Error handling like command: {e}")
            return False
            
    def _handle_batch_like_command(self, command: str, gid: Optional[int], uid: int) -> bool:
        """处理批量点赞命令"""
        try:
            parts = command.split()
            if len(parts) < 2:
                self.qq_service.send_message(gid, "请指定要点赞的用户QQ号列表", uid)
                return True
                
            # 解析QQ号列表
            uids = [int(qq) for qq in parts[1].split(",")]
            times = 10  # 默认点赞次数
            
            if len(parts) > 2:
                times = min(int(parts[2]), 20)
                
            results = self.like_service.batch_send_likes(uids, times)
            
            # 生成结果报告
            success_count = sum(1 for success in results.values() if success)
            message = f"批量点赞完成\n成功: {success_count}\n失败: {len(results) - success_count}"
            
            self.qq_service.send_message(gid, message, uid)
            return True
            
        except ValueError:
            self.qq_service.send_message(gid, "QQ号格式错误", uid)
            return True
        except Exception as e:
            self.logger.error(f"Error handling batch like command: {e}")
            return False
        
    def _handle_bilibili_link(self, message: str, gid: Optional[int], uid: int) -> bool:
        """处理B站链接"""
        try:
            urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', message)
            
            for url in urls:
                if "b23.tv" in url or "bilibili.com" in url:
                    video_details = self.bilibili_service.fetch_video_details(url)
                    if video_details:
                        card_path = self.bilibili_service.create_video_card(video_details)
                        if card_path:
                            # 使用本地文件路径发送图片
                            message = [
                                self.qq_service.image(f"file:///{card_path}")
                            ]
                            self.qq_service.send_message(gid, message, uid)
                            return True
                            
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling bilibili link: {e}")
            return False
        
    def _handle_enable_verification(self, gid: Optional[int], uid: int) -> bool:
        """处理开启验证命令"""
        try:
            if not gid or str(uid) != self.config.qq_bot['admin_qq']:
                return False
                
            if self.verification_service.enable_verification(gid):
                message = [self.qq_service.text("已开启入群验证")]
                self.qq_service.send_message(gid, message, uid)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error enabling verification: {e}")
            return False
            
    def _handle_disable_verification(self, gid: Optional[int], uid: int) -> bool:
        """处理关闭验证命令"""
        try:
            if not gid or str(uid) != self.config.qq_bot['admin_qq']:
                return False
                
            if self.verification_service.disable_verification(gid):
                message = [self.qq_service.text("已关闭入群验证")]
                self.qq_service.send_message(gid, message, uid)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error disabling verification: {e}")
            return False