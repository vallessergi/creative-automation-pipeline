from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict
import uuid
from pathlib import Path
from loguru import logger
from utils import AssetManager, CreativeGenerator, MetricsManager, ContentModerator

app = FastAPI(title="Creative Automation Pipeline", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
asset_manager = AssetManager()
creative_generator = CreativeGenerator()
metrics_manager = MetricsManager()
content_moderator = ContentModerator()

# Global storage for campaign results
campaign_results: Dict[str, dict] = {}

# Basic models
class Product(BaseModel):
    name: str
    description: str

class CampaignBrief(BaseModel):
    products: List[Product]  # At least 2 products required
    target_region: str
    target_audience: str
    campaign_message: str

@app.get("/")
async def root():
    return {"status": "healthy", "message": "Creative Automation Pipeline is running"}

@app.get("/assets/info")
async def get_assets_info():
    """Get information about available assets"""
    return asset_manager.get_asset_info()

@app.get("/campaign/{campaign_id}/images")
async def list_campaign_images(campaign_id: str):
    """List all generated images for a campaign"""
    campaign_dir = Path("output") / campaign_id
    
    if not campaign_dir.exists():
        raise HTTPException(status_code=404, detail="Campaign output not found")
    
    images = {}
    for product_dir in campaign_dir.iterdir():
        if product_dir.is_dir():
            product_images = []
            for image_file in product_dir.glob("*.jpg"):
                product_images.append({
                    "filename": image_file.name,
                    "path": str(image_file.relative_to(Path("."))),
                    "size": image_file.stat().st_size,
                    "aspect_ratio": image_file.stem.split('_')[-1].replace('x', ':')
                })
            images[product_dir.name] = product_images
    
    return {
        "campaign_id": campaign_id,
        "images": images,
        "total_images": sum(len(imgs) for imgs in images.values())
    }

@app.get("/campaign/{campaign_id}/download/{product_name}/{filename}")
async def download_campaign_image(campaign_id: str, product_name: str, filename: str):
    """Download a specific campaign image"""
    image_path = Path("output") / campaign_id / product_name / filename
    
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(
        path=str(image_path),
        media_type="image/jpeg",
        filename=filename
    )

@app.get("/campaigns")
async def list_campaigns():
    """List all available campaign IDs from output folder"""
    output_dir = Path("output")
    campaign_ids = []
    
    if output_dir.exists():
        for campaign_dir in output_dir.iterdir():
            if campaign_dir.is_dir():
                campaign_ids.append(campaign_dir.name)
    
    return campaign_ids

@app.get("/metrics")
async def get_all_metrics():
    """Get metrics for all campaigns"""
    return metrics_manager.list_all_metrics()

@app.get("/campaign/{campaign_id}")
async def get_campaign_result(campaign_id: str):
    """Get specific campaign result"""
    if campaign_id not in campaign_results:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign_results[campaign_id]

@app.post("/generate-campaign")
async def generate_campaign(brief: CampaignBrief, background_tasks: BackgroundTasks):
    """Generate creative campaign from JSON brief"""
    
    # Validate minimum 2 products
    if len(brief.products) < 2:
        raise HTTPException(status_code=400, detail="At least 2 products are required")
    
    # Generate unique campaign ID
    campaign_id = str(uuid.uuid4())[:8]
    
    logger.info(f"Processing campaign {campaign_id} for {len(brief.products)} products")
    
    # Initialize campaign result
    campaign_results[campaign_id] = {
        "campaign_id": campaign_id,
        "status": "processing",
        "brief": brief.dict(),
        "creatives": {},
        "logs": [f"Campaign {campaign_id} started"]
    }
    
    # Add background task to process the campaign
    background_tasks.add_task(process_campaign_async, campaign_id, brief)
    
    return {
        "status": "accepted",
        "campaign_id": campaign_id,
        "message": f"Campaign {campaign_id} is being processed"
    }

async def process_campaign_async(campaign_id: str, brief: CampaignBrief):
    """Background task to process campaign and generate all creatives"""
    try:
        result = campaign_results[campaign_id]
        result["logs"].append("Starting content compliance check")
        
        # Validate campaign content for compliance
        is_compliant, compliance_reason = content_moderator.validate_campaign_content(brief.dict())
        
        if not is_compliant:
            result["status"] = "failed"
            result["logs"].append(f"COMPLIANCE FAILURE: {compliance_reason}")
            
            # Save failed campaign metrics with compliance reason
            metrics_manager.save_campaign_metrics(
                campaign_id=campaign_id,
                campaign_brief=brief.dict(),
                final_status="failed_compliance",
                product_metrics={},
                reason=compliance_reason
            )
            
            logger.error(f"Campaign {campaign_id} failed compliance check: {compliance_reason}")
            return
        
        result["logs"].append("Content compliance check passed")
        result["logs"].append("Starting creative generation")
        
        # Process each product
        for product in brief.products:
            result["logs"].append(f"Processing product: {product.name}")
            
            # Check for existing assets with detailed logging
            existing_assets = asset_manager.check_existing_assets(product.name)
            
            # Log asset discovery status
            if existing_assets:
                result["logs"].append(f"✅ Found {len(existing_assets)} existing assets for {product.name} - REUSING")
                asset_status = "reused"
            else:
                result["logs"].append(f"❌ No existing assets found for {product.name} - WILL GENERATE")
                asset_status = "generated"
            
            # Create product-specific output directory
            product_dir = Path("output") / campaign_id / product.name.lower().replace(" ", "_")
            product_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate creatives for all aspect ratios
            creatives = creative_generator.generate_creative_set(
                product_name=product.name,
                product_description=product.description,
                campaign_message=brief.campaign_message,
                output_dir=product_dir,
                existing_assets=existing_assets
            )
            
            result["creatives"][product.name] = {
                "asset_status": asset_status,
                "existing_assets_found": len(existing_assets),
                "existing_assets_used": existing_assets,
                "generated_creatives": creatives,
                "aspect_ratios": list(creatives.keys())
            }
            
            if asset_status == "reused":
                result["logs"].append(f"✅ Successfully reused assets for {product.name} - {len(creatives)} creatives created")
            else:
                result["logs"].append(f"🤖 Generated new assets for {product.name} - {len(creatives)} creatives created")
        
        # Brand compliance check after generation
        result["logs"].append("Checking brand compliance (background colors)")
        brand_compliant, brand_reason = content_moderator.check_brand_compliance(campaign_id)
        
        if not brand_compliant:
            result["status"] = "failed"
            result["logs"].append(f"BRAND COMPLIANCE FAILURE: {brand_reason}")
            
            # Save failed campaign metrics with brand compliance reason
            metrics_manager.save_campaign_metrics(
                campaign_id=campaign_id,
                campaign_brief=brief.dict(),
                final_status="failed_brand_compliance",
                product_metrics=result["creatives"],
                reason=brand_reason
            )
            result["logs"].append("Campaign metrics saved")
            
            logger.error(f"Campaign {campaign_id} failed brand compliance: {brand_reason}")
            return
        
        result["status"] = "completed"
        result["logs"].append("Brand compliance check passed")
        result["logs"].append("Campaign processing completed successfully")
        
        # Save campaign metrics
        metrics_manager.save_campaign_metrics(
            campaign_id=campaign_id,
            campaign_brief=brief.dict(),
            final_status="completed",
            product_metrics=result["creatives"],
            reason="Campaign successfully completed with all creatives generated"
        )
        result["logs"].append("Campaign metrics saved")
        
        logger.info(f"Campaign {campaign_id} completed successfully")
        
    except Exception as e:
        result["status"] = "failed"
        result["logs"].append(f"Error: {str(e)}")
        
        # Save failed campaign metrics
        metrics_manager.save_campaign_metrics(
            campaign_id=campaign_id,
            campaign_brief=brief.dict(),
            final_status="failed_technical",
            product_metrics=result.get("creatives", {}),
            reason=f"Technical error during campaign processing: {str(e)}"
        )
        
        logger.error(f"Campaign {campaign_id} failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)