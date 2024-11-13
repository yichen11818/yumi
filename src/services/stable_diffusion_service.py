import replicate
from typing import Optional, List
from utils.config import Config
from utils.logger import Logger

class StableDiffusionService:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.client = replicate.Client(api_token=self.config.replicate['api_token'])
        self.model = self.client.models.get("stability-ai/stable-diffusion")
        
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