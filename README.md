# Creative Automation Pipeline

A full-stack automation system for generating social media creative assets, featuring AI-powered content moderation, GenAI image generation, and a modern React frontend with AWS Cloudscape Design System.

## Overview

This system automates the creation of social media creatives by:
- Providing a modern web interface for campaign management
- Accepting campaign briefs through forms or JSON API
- **AI-powered content compliance validation** using Groq's Llama 3.1 model
- **GenAI image generation** using Replicate's Flux model when assets are unavailable
- Reusing existing assets when available
- Generating multiple aspect ratios (1:1, 9:16, 16:9)
- Adding campaign message overlays with responsive text
- Organizing outputs by product and aspect ratio
- Tracking campaign metrics and performance

## Quick Start

### Prerequisites
- Docker & Docker Compose (required)
- **Groq API Key** (free) - Get from [console.groq.com](https://console.groq.com/)
- **Replicate API Token** - Get from [replicate.com](https://replicate.com/)

### Installation

1. **Configure API Keys** in `backend/app.py`:
```python
# Replace with your actual API keys
GROQ_API_KEY = "your_groq_api_key_here"
REPLICATE_API_TOKEN = "your_replicate_api_token_here"
```

2. **Run the complete stack**:
```bash
docker-compose up --build
```

The application will be available at:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

## Usage

### Web Interface (Recommended)

1. **Access the frontend** at `http://localhost:3000`
2. **Upload Assets (Optional)**:
   - Navigate to the Upload tab
   - Upload product images via the form interface
   - System automatically organizes assets by product name
3. **Create Campaign Brief**:
   - Fill out the campaign form with 2+ products
   - Add product names and descriptions
   - Set target region and audience
   - Enter your campaign message
4. **Submit and Monitor**:
   - Click "Generate Campaign"
   - **AI performs intelligent content compliance validation**
   - System reuses uploaded assets or **generates AI images** if none available
   - View real-time processing status and logs
   - Navigate to Downloads tab to access generated assets
5. **View Results**:
   - Browse generated creatives by campaign
   - Download individual assets or view metrics

### API Usage (Alternative)

#### 1. Create Campaign Brief JSON

Create a JSON file with your campaign details:

```json
{
  "products": [
    {
      "name": "EcoClean Detergent",
      "description": "Environmentally friendly laundry detergent made from natural ingredients."
    },
    {
      "name": "FreshAir Fabric Softener", 
      "description": "Natural fabric softener with essential oils."
    }
  ],
  "target_region": "North America",
  "target_audience": "Environmentally conscious families with children, ages 25-45",
  "campaign_message": "Clean your family's clothes the natural way. Gentle on skin, tough on stains, kind to the planet."
}
```

### 2. Submit Campaign

**Using curl**:
```bash
curl -X POST "http://localhost:8000/generate-campaign" \
  -H "Content-Type: application/json" \
  -d @example_campaign_brief.json
```

**Response**:
```json
{
  "status": "accepted",
  "campaign_id": "a1b2c3d4",
  "message": "Campaign a1b2c3d4 is being processed"
}
```

### 3. Check Campaign Status

```bash
curl "http://localhost:8000/campaign/a1b2c3d4"
```

### 4. View Results

Generated creatives will be saved in:
```
output/
└── a1b2c3d4/
    ├── ecoClean_detergent/
    │   ├── ecoClean_detergent_1x1.jpg
    │   ├── ecoClean_detergent_9x16.jpg
    │   └── ecoClean_detergent_16x9.jpg
    └── freshair_fabric_softener/
        ├── freshair_fabric_softener_1x1.jpg
        ├── freshair_fabric_softener_9x16.jpg
        └── freshair_fabric_softener_16x9.jpg
```

## Asset Management

### Method 1: Upload Assets via API

Upload product images through the web interface or API:

**Via Web Interface:**
- Navigate to the Upload tab in the frontend
- Select product name and image file
- Upload directly through the form

**Via API:**
```bash
curl -X POST "http://localhost:8000/assets/upload" \
  -F "product_name=EcoClean Detergent" \
  -F "image=@path/to/your/image.jpg"
```

**Response:**
```json
{
  "status": "success",
  "message": "Image uploaded successfully for product 'EcoClean Detergent'",
  "file_info": {
    "filename": "image.jpg",
    "size": 124567,
    "path": "assets/ecoClean_detergent/image.jpg"
  }
}
```

### Method 2: Manual Asset Placement

Place existing product images directly in the `assets/` directory:

```
assets/
├── ecoClean_detergent/
│   ├── product_photo1.jpg
│   └── product_photo2.png
└── freshair_fabric_softener/
    └── bottle_image.jpg
```

### Asset Discovery

The system automatically uses existing assets instead of AI generation. Check available assets:

```bash
curl "http://localhost:8000/assets/info"
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/generate-campaign` | POST | Submit campaign brief |
| `/campaign/{campaign_id}` | GET | Get campaign status/results |
| `/campaigns` | GET | List all available campaign IDs |
| `/campaign/{campaign_id}/images` | GET | List all generated images for a campaign |
| `/campaign/{campaign_id}/download/{product_name}/{filename}` | GET | Download a specific campaign image |
| `/assets/upload` | POST | **Upload product assets via form (multipart/form-data)** |
| `/assets/info` | GET | Get information about available assets |
| `/metrics` | GET | Get metrics for all campaigns |

## Key Design Decisions

### 1. **Modular Architecture**
**Backend (FastAPI):**
- **`app.py`**: FastAPI server orchestrating the pipeline
- **`asset_manager.py`**: Handles file organization and asset discovery
- **`creative_generator.py`**: Combines images, resizing, and text overlays
- **`image_generator.py`**: AI-powered image generation (Replicate Flux)
- **`content_moderator.py`**: AI-powered content validation (Groq Llama 3.1)
- **`metrics_manager.py`**: Campaign performance tracking

**Frontend (React):**
- **`App.jsx`**: Main application with AWS Cloudscape UI
- **`CampaignBriefForm.jsx`**: Campaign creation interface
- **`CampaignResults.jsx`**: Real-time status and results display
- **`DownloadsPage.jsx`**: Asset browsing and download interface
- **`MetricsPage.jsx`**: Campaign analytics and metrics

### 2. **Asset Strategy**
- **Primary**: Use existing assets from `/assets` folder
- **Fallback**: **AI-generated images using Replicate's Flux model**

### 3. **Aspect Ratio Handling**
- **1:1 (1080x1080)**: Instagram posts, Facebook
- **9:16 (1080x1920)**: Instagram stories, TikTok
- **16:9 (1920x1080)**: YouTube, Facebook covers

### 4. **Text Overlay Design**
- Semi-transparent dark overlay at bottom for readability
- Responsive font sizing based on image dimensions
- Word wrapping to prevent text overflow
- Product name at top, campaign message at bottom

### 5. **AI-Powered Compliance Pipeline**
- **Pre-generation**: **AI-powered content validation using Groq's Llama 3.1 model**
- **Intelligent Analysis**: Context-aware policy violation detection for discriminatory content, illegal content, false claims, and excessive promotional language
- **Advanced Reasoning**: AI provides detailed explanations for policy violations instead of simple keyword matching
- **Failure Handling**: Campaigns fail safely with detailed AI reasoning and logging
- **Metrics Integration**: AI compliance results tracked and reported
- **✅ Production Ready**: Uses sophisticated LLM for real-world content moderation

### 6. **Asynchronous Processing**
- Background tasks for campaign generation
- Non-blocking API responses
- Real-time status tracking with detailed logs
- Comprehensive error handling and recovery

## AI Integration

### Content Moderation (Groq)
- **Model**: Llama 3.1 8B Instant (free tier available)
- **Capabilities**:
  - Discriminatory content detection
  - Illegal content screening
  - False claims identification
  - Excessive promotional language analysis
- **Context-Aware**: Understands nuance vs. simple keyword matching
- **API**: Requires free Groq API key from [console.groq.com](https://console.groq.com/)

### Image Generation (Replicate)
- **Model**: Flux Dev by Black Forest Labs
- **Quality**: Professional product photography with studio lighting
- **Customization**: Generates based on product name and description
- **Fallback**: Only used when existing assets unavailable
- **API**: Requires Replicate API token from [replicate.com](https://replicate.com/)

## Assumptions and Limitations

### Assumptions
- **Minimum 2 products** required per campaign
- **English text** support (could be extended for localization)
- **Standard social media dimensions** for aspect ratios
- **JPEG output format** for broad compatibility
- **Ephemeral Usage**: Data persistence not required between container restarts
- **Development Environment**: Not intended for production use without significant enhancements

### Current Limitations

1. **Storage & Data Persistence**:
   - **Ephemeral Storage**: All data (assets, outputs, metrics) disappears when containers are recreated
   - **No Volume Persistence**: Docker volumes not configured for data retention
   - **Local File System Only**: No cloud storage or database integration

2. **Compliance System (Mock Implementation)**:
   - **No Brand Intelligence**: Brand compliance checks are in place

3. **Image Generation**:
   - **AI-Powered**: Uses Replicate's Flux Dev model for professional-quality image generation
   - **Professional Quality**: Generates product photography with studio lighting and clean backgrounds
   - **Generation Time**: AI image creation takes 10-30 seconds per image
   - Asset reuse prioritized over generation for efficiency and cost optimization

4. **Text Rendering**:
   - Basic font support (system fonts only)
   - Limited typography customization
   - No brand font loading

5. **Processing & Scalability**:
   - Single-threaded processing
   - No batch processing optimization
   - Limited error recovery
   - No horizontal scaling capabilities

## Future Enhancements

### Critical Production Requirements
- [x] **GenAI Image Generation**: ✅ **COMPLETED** - Uses Replicate's Flux Dev model for professional image generation
- [ ] **Data Persistence**: Docker volumes or database integration for data retention
- [x] **AI-Powered Compliance**: ✅ **COMPLETED** - Uses Groq's Llama 3.1 for intelligent content validation
- [ ] **Computer Vision Compliance**: Image analysis for brand guideline validation (basic brand checks removed)
- [ ] **Cloud Storage**: S3/GCS integration with persistent asset management
- [ ] **Database Integration**: PostgreSQL/MongoDB for campaign and metrics storage

### Additional Planned Features
- [ ] **Multi-language**: Localized campaign messages
- [ ] **Batch Processing**: Multiple campaigns simultaneously
- [ ] **Custom Fonts**: Brand typography support
- [ ] **A/B Testing**: Multiple creative variations
- [ ] **Advanced Brand Intelligence**: Logo detection, color palette validation
- [ ] **Legal Content Analysis**: Context-aware content screening

### Integration Options
- **CMS Integration**: Connect to content management systems
- **Social Media APIs**: Direct posting to platforms
- **Analytics**: Performance tracking and optimization
- **Approval Workflows**: Review and approval processes

## Troubleshooting

### Common Issues

1. **Data Loss After Container Restart**:
   - **Issue**: All generated campaigns, assets, and metrics disappear when containers are recreated
   - **Cause**: No persistent Docker volumes configured
   - **Workaround**: Copy important data out of containers before stopping: `docker cp container_name:/app/backend/output ./backup`

2. **Container Issues**: Ensure Docker and Docker Compose are installed and running

3. **Font Issues**: System falls back to default fonts if custom fonts unavailable

4. **Permission Errors**: Ensure write permissions for `backend/assets/` and `backend/output/` directories

5. **Port Conflicts**: Check that ports 3000 and 8000 are available

6. **AI API Dependencies**:
   - **Issue**: Content moderation or image generation may fail
   - **Cause**: Missing or invalid API keys for Groq/Replicate
   - **Solution**: Ensure valid API keys are configured in `backend/app.py`

7. **Rate Limiting**:
   - **Issue**: AI services may temporarily reject requests
   - **Cause**: Free tier rate limits on Groq or Replicate
   - **Solution**: Wait and retry, or upgrade to paid tiers

### Debug Mode
Set environment variable for detailed logging:
```bash
export LOG_LEVEL=DEBUG
python app.py
```

## Development

### Project Structure
```
├── docker-compose.yml           # Container orchestration
├── example_campaign_brief.json  # Sample campaign data
├── test_pipeline.py            # Backend testing script
├── README.md                   # This documentation
│
├── backend/                    # FastAPI backend
│   ├── app.py                 # Main FastAPI application
│   ├── Dockerfile             # Backend container config
│   ├── requirements.txt       # Python dependencies
│   ├── utils/                 # Modular utilities
│   │   ├── asset_manager.py   # Asset discovery and organization
│   │   ├── creative_generator.py # Image processing and overlays
│   │   ├── image_generator.py # Placeholder image creation
│   │   ├── content_moderator.py # Compliance validation
│   │   └── metrics_manager.py # Performance tracking
│   ├── assets/                # Input assets (optional)
│   │   ├── water/
│   │   └── coca_cola/
│   ├── output/                # Generated creatives
│   │   ├── campaign_id1/
│   │   └── campaign_id2/
│   └── metrics/               # Campaign performance data
│
└── frontend/                  # React frontend
    ├── src/
    │   ├── App.jsx           # Main application
    │   ├── components/       # UI components
    │   └── services/         # API integration
    ├── Dockerfile            # Frontend container config
    ├── package.json          # Node.js dependencies
    ├── vite.config.js        # Build configuration
    └── nginx.conf            # Production web server config
```

### Adding New Features

1. **New Aspect Ratios**: Modify `aspect_ratios` dict in `creative_generator.py`
2. **New GenAI Providers**: Extend `image_generator.py` with new APIs
3. **Brand Compliance**: Add validation functions to pipeline
4. **Custom Fonts**: Update text rendering in `creative_generator.py`

## License

This is a proof-of-concept implementation for demonstration purposes.