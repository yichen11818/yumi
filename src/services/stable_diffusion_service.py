import replicate
from typing import Optional, List
from utils.config import Config
from utils.logger import Logger
import os

class StableDiffusionService:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        
        # 设置环境变量
        os.environ["PYTHONIOENCODING"] = "utf-8"
        os.environ["REPLICATE_API_TOKEN"] = self.config.replicate.get("api_token")
        
        try:
            # 创建客户端时设置headers
            import httpx
            headers = {
                "Authorization": f"Token {self.config.replicate.get('api_token')}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # 使用自定义的transport
            transport = httpx.HTTPTransport(retries=3)
            self.client = replicate.Client(
                transport=transport,
                headers=headers
            )
            
            # 初始化模型
            try:
                self.model = self.client.models.get("stability-ai/stable-diffusion")
                self.logger.info("StableDiffusion model initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize StableDiffusion model: {e}")
                self.model = None
                
        except Exception as e:
            self.logger.error(f"Failed to initialize StableDiffusion service: {e}")
            self.client = None
            self.model = None
        
    def generate_image(self, prompt: str, negative_prompt: str = "", num_outputs: int = 1) -> Optional[List[str]]:
        """生成图像"""
        try:
            output = self.model.predict(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_outputs=num_outputs,
                num_inference_steps=50,
                guidance_scale=7.5,
                width=512,
                height=512
            )
            return output
        except Exception as e:
            self.logger.error(f"Error generating image with Stable Diffusion: {e}")
            return None