from PIL import Image, ImageDraw, ImageFont
import requests
from pathlib import Path
from typing import Tuple
from loguru import logger
import os
import random
import replicate

class ImageGenerator:
    def __init__(self, replicate_api_token: str):
        self.replicate_api_token = replicate_api_token
        self.replicate_client = replicate.Client(api_token=replicate_api_token)
        
    def generate_with_replicate(self, product_name: str, product_description: str, aspect_ratio: str = "1:1") -> str:
        """Generate image using Replicate API"""
        try:
            prompt = f"Professional high-quality product photography of {product_name}. {product_description}. Clean white background, professional studio lighting, commercial photography, 4K resolution, product catalog style"
            
            output = self.replicate_client.run(
                "black-forest-labs/flux-dev",
                input={
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio,
                    "output_format": "jpg",
                    "output_quality": 90,
                    "num_inference_steps": 28
                }
            )
            
            image_url = output if isinstance(output, str) else output[0] if isinstance(output, list) else None
            if image_url:
                logger.info(f"Generated image with Replicate for {product_name}")
                return image_url
            else:
                raise ValueError(f"No valid image URL returned from Replicate for {product_name}")
                
        except Exception as e:
            logger.error(f"Replicate generation failed: {str(e)}")
            raise
    
    def download_image_from_url(self, url: str, save_path: Path) -> bool:
        """Download image from URL and save to path"""
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded image to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download image: {str(e)}")
            return False
    
    def generate_product_image(self,
                             product_name: str,
                             product_description: str,
                             campaign_message: str,
                             output_path: Path,
                             size: Tuple[int, int] = None,
                             aspect_ratio: str = "1:1") -> bool:
        """Generate or create product image and save to output path"""
        try:
            image_url = self.generate_with_replicate(product_name, product_description, aspect_ratio)
            if self.download_image_from_url(image_url, output_path):
                return True
            else:
                logger.error(f"Failed to download image for {product_name}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to generate image for {product_name}: {str(e)}")
            return False
