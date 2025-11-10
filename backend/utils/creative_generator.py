from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Tuple, List, Dict
from loguru import logger
from .image_generator import ImageGenerator
from .asset_manager import AssetManager

class CreativeGenerator:
    def __init__(self, image_generator: ImageGenerator, asset_manager: AssetManager):
        self.image_generator = image_generator
        self.asset_manager = asset_manager
        self.aspect_ratios = {
            "1:1": (1080, 1080), 
            "9:16": (1080, 1920),
            "16:9": (1920, 1080)
        }
    
    def resize_image_to_aspect_ratio(self, image: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """Resize image to target aspect ratio while maintaining quality"""
        # Calculate the aspect ratios
        original_ratio = image.width / image.height
        target_ratio = target_size[0] / target_size[1]
        
        if original_ratio > target_ratio:
            # Image is wider than target, fit by height
            new_height = target_size[1]
            new_width = int(new_height * original_ratio)
        else:
            # Image is taller than target, fit by width
            new_width = target_size[0]
            new_height = int(new_width / original_ratio)
        
        # Resize image
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create new image with target size and center the resized image
        final_image = Image.new("RGB", target_size, (255, 255, 255))
        
        # Calculate position to center the image
        x = (target_size[0] - new_width) // 2
        y = (target_size[1] - new_height) // 2
        
        final_image.paste(resized, (x, y))
        return final_image
    
    def add_text_overlay(self,
                        image: Image.Image,
                        campaign_message: str,
                        product_name: str) -> Image.Image:
        """Add campaign message text overlay to image"""
        # Create a copy to avoid modifying original
        img_with_text = image.copy()
        draw = ImageDraw.Draw(img_with_text)
        
        # Get image dimensions
        width, height = img_with_text.size
        
        # Try to load a font, fall back to default
        try:
            font_size = width // 25  # Responsive font size
            font = ImageFont.truetype("arial.ttf", font_size)
            small_font = ImageFont.truetype("arial.ttf", font_size // 2)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Create semi-transparent overlay for text readability
        overlay = Image.new('RGBA', img_with_text.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Add dark overlay at bottom for text
        overlay_height = height // 4
        overlay_draw.rectangle([0, height - overlay_height, width, height],
                             fill=(0, 0, 0, 180))
        
        # Composite overlay onto image
        img_with_text = Image.alpha_composite(img_with_text.convert('RGBA'), overlay)
        img_with_text = img_with_text.convert('RGB')
        
        # Redraw on the composite image
        draw = ImageDraw.Draw(img_with_text)
        
        # Add campaign message
        message_y = height - overlay_height + 20
        self._draw_wrapped_text(draw, campaign_message, 20, message_y, width - 40, font, "white")
        
        # Add product name at top
        product_y = 20
        self._draw_wrapped_text(draw, product_name.upper(), 20, product_y, width - 40, small_font, "white")
        
        return img_with_text
    
    def _draw_wrapped_text(self, draw, text: str, x: int, y: int, max_width: int, font, fill: str):
        """Draw text with word wrapping"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]
            
            if line_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)  # Single word is too long, add anyway
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw each line
        line_height = 30
        for i, line in enumerate(lines):
            draw.text((x, y + i * line_height), line, fill=fill, font=font)
    
    def generate_creative_set(self, 
                            product_name: str,
                            product_description: str,
                            campaign_message: str,
                            output_dir: Path,
                            existing_assets: List[str] = None) -> Dict[str, str]:
        """Generate complete set of creatives for all aspect ratios"""
        results = {}
        
        # Use existing asset if available, otherwise generate asset set
        if existing_assets and len(existing_assets) > 0:
            logger.info(f"Using existing asset for {product_name}: {existing_assets[0]}")
            try:
                base_image = Image.open(existing_assets[0])
            except Exception as e:
                logger.error(f"Failed to load existing asset: {e}")
                base_image = None
        else:
            # No existing assets - generate with AI image
            logger.info(f"No assets found for {product_name}, generating single asset")
            # Create product asset directory
            product_dir = Path("assets") / product_name.lower().replace(" ", "_")
            product_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate a AI image
            image_path = product_dir / "product_1.jpg"
            success = self.image_generator.generate_product_image(product_name, product_description, "", image_path)
            
            if success:
                logger.info(f"Using newly generated asset: {image_path}")
                try:
                    base_image = Image.open(image_path)
                except Exception as e:
                    logger.error(f"Failed to load newly created asset: {e}")
                    return results
            else:
                logger.error(f"Failed to generate asset for {product_name}")
                return results
        
        # Generate creatives for each aspect ratio using AI img2img model
        # Get the base image path for img2img generation
        if existing_assets and len(existing_assets) > 0:
            base_image_path = existing_assets[0]
        else:
            base_image_path = str(product_dir / "product_1.jpg")
        
        for ratio_name, target_size in self.aspect_ratios.items():
            try:
                # Generate variant using img2img model with target aspect ratio
                logger.info(f"Generating {ratio_name} variant using img2img model")
                img_prompt = f"Professional product photography of {product_name}, {product_description}, high quality, clean background, studio lighting"
                
                variant_image_url = self.image_generator.generate_img2img_variant(
                    input_image_path=base_image_path,
                    aspect_ratio=ratio_name,
                    prompt=img_prompt
                )
                
                # Download the variant image
                temp_variant_path = output_dir / f"temp_variant_{ratio_name.replace(':', 'x')}.jpg"
                if self.image_generator.download_image_from_url(variant_image_url, temp_variant_path):
                    # Load the downloaded variant image
                    variant_image = Image.open(temp_variant_path)
                    
                    # Add text overlay (unchanged - still using Python)
                    final_creative = self.add_text_overlay(variant_image, campaign_message, product_name)
                    
                    # Save final creative
                    filename = f"{product_name.lower().replace(' ', '_')}_{ratio_name.replace(':', 'x')}.jpg"
                    output_path = output_dir / filename
                    final_creative.save(output_path, quality=95)
                    
                    # Clean up temp file
                    temp_variant_path.unlink()
                    
                    results[ratio_name] = str(output_path)
                    logger.info(f"Generated creative using img2img: {output_path}")
                else:
                    logger.error(f"Failed to download img2img variant for {ratio_name}")
                
            except Exception as e:
                logger.error(f"Failed to generate {ratio_name} creative for {product_name}: {str(e)}")
        
        return results