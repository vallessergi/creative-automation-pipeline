from PIL import Image, ImageDraw, ImageFont
import requests
from pathlib import Path
from typing import Tuple, Optional
from loguru import logger
import os
import random

class ImageGenerator:
    def __init__(self):
        self.default_size = (1024, 1024)
        # You can set OpenAI API key as environment variable
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
    def generate_placeholder_image(self, 
                                 product_name: str, 
                                 product_description: str,
                                 size: Tuple[int, int] = None) -> Image.Image:
        """Generate a simple placeholder image when GenAI is not available"""
        if size is None:
            size = self.default_size
            
        # Create a colored background - randomized from specified colors
        colors = ["#00FF00", "#FF0000", "#0000FF", "#FFFF00"]  # Green, Red, Blue, Yellow
        color = random.choice(colors)
        
        image = Image.new("RGB", size, color)
        draw = ImageDraw.Draw(image)
        
        # Try to use a font, fall back to default if not available
        try:
            font_size = min(size) // 15
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Add product name text
        text = f"{product_name}\nProduct Image"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        draw.text((x, y), text, fill="white", font=font, align="center")
        
        logger.info(f"Generated placeholder image for {product_name}")
        return image
    
    def generate_with_openai(self, 
                           product_name: str, 
                           product_description: str,
                           campaign_message: str,
                           size: str = "1024x1024") -> Optional[str]:
        """Generate image using OpenAI DALL-E (if API key is available)"""
        if not self.openai_api_key:
            logger.warning("OpenAI API key not found, using placeholder")
            return None
            
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            prompt = f"Professional product advertisement for {product_name}. {product_description}. Style: modern, clean, commercial advertising. High quality, professional lighting."
            
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            logger.info(f"Generated image with OpenAI for {product_name}")
            return image_url
            
        except Exception as e:
            logger.error(f"OpenAI image generation failed: {str(e)}")
            return None
    
    def download_image_from_url(self, url: str, save_path: Path) -> bool:
        """Download image from URL and save to path"""
        try:
            response = requests.get(url, timeout=30)
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
            # Try OpenAI first if API key is available
            if self.openai_api_key:
                image_url = self.generate_with_openai(
                    product_name, 
                    product_description, 
                    campaign_message
                )
                if image_url and self.download_image_from_url(image_url, output_path):
                    return True
            
            # Fall back to placeholder
            if size is None:
                size = self.default_size
                
            placeholder_image = self.generate_placeholder_image(
                product_name, 
                product_description, 
                size
            )
            placeholder_image.save(output_path)
            
            logger.info(f"Saved image to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate image for {product_name}: {str(e)}")
            return False

    def generate_product_asset_set(self, product_name: str, product_description: str) -> bool:
        """Generate 3 placeholder images for a product with no existing assets"""
        try:
            # Create product asset directory
            product_dir = Path("assets") / product_name.lower().replace(" ", "_")
            product_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate 3 different placeholder images with randomized colors
            colors = ["#00FF00", "#FF0000", "#0000FF", "#FFFF00"]  # Green, Red, Blue, Yellow
            variations = [
                {"name": "product_1", "color": random.choice(colors), "size": (300, 300)},
                {"name": "product_2", "color": random.choice(colors), "size": (400, 300)},
                {"name": "product_3", "color": random.choice(colors), "size": (300, 400)}
            ]
            
            for variation in variations:
                image = self.generate_placeholder_image(
                    product_name, 
                    product_description, 
                    variation["size"]
                )
                
                # Change background color
                colored_image = Image.new("RGB", variation["size"], variation["color"])
                draw = ImageDraw.Draw(colored_image)
                
                # Add product text
                try:
                    font_size = min(variation["size"]) // 15
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                
                text = f"{product_name}\n{variation['name'].replace('_', ' ').title()}"
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (variation["size"][0] - text_width) // 2
                y = (variation["size"][1] - text_height) // 2
                
                draw.text((x, y), text, fill="white", font=font, align="center")
                
                # Save the image
                image_path = product_dir / f"{variation['name']}.jpg"
                colored_image.save(image_path)
                logger.info(f"Generated placeholder asset: {image_path}")
            
            logger.info(f"Generated 3 placeholder assets for {product_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate asset set for {product_name}: {str(e)}")
            return False