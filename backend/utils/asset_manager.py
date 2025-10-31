from pathlib import Path
from typing import List, Dict
from loguru import logger

class AssetManager:
    def __init__(self, assets_dir: str = "assets", output_dir: str = "output"):
        self.assets_dir = Path(assets_dir)
        self.output_dir = Path(output_dir)
        self._setup_directories()
    
    def _setup_directories(self):
        """Create necessary directories if they don't exist"""
        self.assets_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"Asset directories setup: {self.assets_dir}, {self.output_dir}")
    
    def check_existing_assets(self, product_name: str) -> List[str]:
        """Check what assets exist for a product"""
        product_dir = self.assets_dir / product_name.lower().replace(" ", "_")
        existing_assets = []
        
        if product_dir.exists():
            # Look for image files
            image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp']
            all_files = list(product_dir.glob("*"))
            
            for file_path in all_files:
                if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                    existing_assets.append(str(file_path))
        
        logger.info(f"Asset scan for {product_name}: Found {len(existing_assets)} image files in {product_dir}")
        return existing_assets
    
    def get_asset_info(self) -> Dict:
        """Get summary of available assets"""
        info = {
            "assets_directory": str(self.assets_dir),
            "output_directory": str(self.output_dir),
            "products_with_assets": []
        }
        
        if self.assets_dir.exists():
            for product_dir in self.assets_dir.iterdir():
                if product_dir.is_dir():
                    asset_count = len([f for f in product_dir.glob("*.*")
                                    if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']])
                    if asset_count > 0:  # Only show products with actual assets
                        info["products_with_assets"].append({
                            "product": product_dir.name,
                            "asset_count": asset_count
                        })
        
        return info
    