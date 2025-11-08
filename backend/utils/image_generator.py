from PIL import Image, ImageDraw, ImageFont
import requests
from pathlib import Path
from typing import Tuple, Optional
from loguru import logger
import os
import random
import replicate

class ImageGenerator:
    def __init__(self, replicate_api_token: str):
        self.default_size = (1024, 1024)
        self.replicate_api_token = replicate_api_token
        self.replicate_client = replicate.Client(api_token=replicate_api_token)
        
    def generate_with_replicate(self, product_name: str, product_description: str) -> Optional[str]:
        """Generate image using Replicate API"""
        try:
            prompt = f"Professional high-quality product photography of {product_name}. {product_description}. Clean white background, professional studio lighting, commercial photography, 4K resolution, product catalog style"
            
            output = self.replicate_client.run(
                "black-forest-labs/flux-dev",
                input={
                    "prompt": prompt,
                    "aspect_ratio": "1:1",
                    "output_format": "jpg",
                    "output_quality": 90,
                    "num_inference_steps": 28
                }
            )
            
            image_url = output if isinstance(output, str) else output[0] if isinstance(output, list) else None
            if image_url:
                logger.info(f"Generated image with Replicate for {product_name}")
                return image_url
                
        except Exception as e:
            logger.error(f"Replicate generation failed: {str(e)}")
            
        return None
    
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
                             size: Tuple[int, int] = None) -> bool:
        """Generate or create product image and save to output path"""
        try:
            image_url = self.generate_with_replicate(product_name, product_description)
            if image_url and self.download_image_from_url(image_url, output_path):
                return True
            else:
                logger.error(f"Failed to generate image with Replicate for {product_name}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to generate image for {product_name}: {str(e)}")
            return False

    def generate_product_asset_set(self, product_name: str, product_description: str) -> bool:
        """Generate 3 AI images for a product with no existing assets"""
        try:
            # Create product asset directory
            product_dir = Path("assets") / product_name.lower().replace(" ", "_")
            product_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate 3 AI images
            variations = ["product_1", "product_2", "product_3"]
            
            for variation in variations:
                image_path = product_dir / f"{variation}.jpg"
                image_url = self.generate_with_replicate(product_name, product_description)
                
                if image_url and self.download_image_from_url(image_url, image_path):
                    logger.info(f"Generated AI asset: {image_path}")
                else:
                    logger.error(f"Failed to generate AI asset for {variation}")
                    return False
            
            logger.info(f"Generated 3 AI assets for {product_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate asset set for {product_name}: {str(e)}")
            return False