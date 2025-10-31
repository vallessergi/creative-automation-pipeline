import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from loguru import logger

class MetricsManager:
    def __init__(self, metrics_dir: str = "metrics"):
        self.metrics_dir = Path(metrics_dir)
        self._setup_directory()
    
    def _setup_directory(self):
        """Create metrics directory if it doesn't exist"""
        self.metrics_dir.mkdir(exist_ok=True)
        logger.info(f"Metrics directory setup: {self.metrics_dir}")
    
    def save_campaign_metrics(self,
                            campaign_id: str,
                            campaign_brief: Dict,
                            final_status: str,
                            product_metrics: Dict,
                            reason: str = "") -> bool:
        """Save campaign metrics to JSON file"""
        try:
            metrics = {
                "campaign_id": campaign_id,
                "timestamp": datetime.now().isoformat(),
                "campaign_brief": {
                    "products": [{"name": p["name"], "description": p["description"]} for p in campaign_brief["products"]],
                    "target_region": campaign_brief["target_region"],
                    "target_audience": campaign_brief["target_audience"],
                    "campaign_message": campaign_brief["campaign_message"]
                },
                "final_status": final_status,
                "reason": reason,
                "product_metrics": product_metrics,
                "summary": {
                    "total_products": len(campaign_brief["products"]),
                    "products_with_existing_assets": sum(1 for p in product_metrics.values() if p["asset_status"] == "reused"),
                    "products_with_generated_assets": sum(1 for p in product_metrics.values() if p["asset_status"] == "generated"),
                    "total_creatives_generated": sum(len(p["aspect_ratios"]) for p in product_metrics.values())
                }
            }
            
            # Save to JSON file
            metrics_file = self.metrics_dir / f"{campaign_id}_metrics.json"
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Campaign metrics saved: {metrics_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save metrics for campaign {campaign_id}: {str(e)}")
            return False
    
    def get_campaign_metrics(self, campaign_id: str) -> Dict:
        """Load campaign metrics from JSON file"""
        metrics_file = self.metrics_dir / f"{campaign_id}_metrics.json"
        
        if not metrics_file.exists():
            return None
        
        try:
            with open(metrics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load metrics for campaign {campaign_id}: {str(e)}")
            return None
    
    def list_all_metrics(self) -> List[Dict]:
        """Get metrics for all campaigns"""
        all_metrics = []
        
        for metrics_file in self.metrics_dir.glob("*_metrics.json"):
            try:
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    metrics = json.load(f)
                    all_metrics.append(metrics)
            except Exception as e:
                logger.error(f"Failed to load metrics from {metrics_file}: {str(e)}")
        
        # Sort by timestamp (newest first)
        all_metrics.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return all_metrics