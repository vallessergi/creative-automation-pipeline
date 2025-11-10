# Creative Automation Pipeline

A full-stack automation system for generating social media creative assets, featuring AI-powered content moderation, GenAI image generation, and a modern React frontend with AWS Cloudscape Design System.

## Overview

This system automates the creation of social media creatives by:
- Providing a modern web interface for campaign management
- Accepting campaign briefs through forms or JSON API
- **AI-powered content compliance validation** using Groq's Llama 3.1 model
- **AI-powered hero image generation** using Replicate's Flux model when assets are unavailable
- Reusing existing assets when available
- Generating multiple aspect ratios (1:1, 9:16, 16:9) with img2img enhancement
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
   - System reuses uploaded assets or **generates single hero image** if none available
   - **AI img2img model enhances assets** while maintaining aspect ratios
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
**Note**: All variants maintain the hero image's original aspect ratio due to img2img model limitations.

## Campaign Asset Generation Workflow

### AI-Powered Asset Pipeline

The system uses a sophisticated AI pipeline to generate campaign assets:

1. **Hero Image Acquisition**:
   - **Existing Assets**: Uses uploaded product images as hero images
   - **AI Generation**: Creates single hero image using Flux Dev model if no assets available

2. **Aspect Ratio Variants via Img2Img**:
   - **Input**: Single hero image (any aspect ratio)
   - **Process**: AI img2img model enhances image quality while maintaining same aspect ratio
   - **Models**: Uses `bxclib2/flux_img2img` for visual enhancement
   - **Limitation**: **Maintains hero image's original aspect ratio** (does not change dimensions)

3. **Text Overlay Application**:
   - **Python Rendering**: Responsive text overlays on each variant
   - **Design**: Semi-transparent backgrounds for optimal readability
   - **Content**: Product name and campaign message positioning

### Benefits of Img2Img Approach
- **Visual Enhancement**: AI improves image quality and style consistency
- **Intelligent Processing**: Better than simple file copying
- **Efficiency**: Single hero → enhanced campaign assets
- **Quality**: Professional AI enhancement of source images

### Img2Img Limitation
- **⚠️ Aspect Ratio Constraint**: The img2img model maintains the **same aspect ratio as the hero image**
- **Impact**: All generated variants (1:1, 9:16, 16:9) will have the hero image's original dimensions
- **Workaround**: Use hero images with desired aspect ratios, or combine with text-to-image generation

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
- **`creative_generator.py`**: AI-powered campaign asset generation using img2img model
- **`image_generator.py`**: AI-powered image generation
- **`content_moderator.py`**: AI-powered content validation (Groq Llama 3.1)
- **`metrics_manager.py`**: Campaign performance tracking

**Frontend (React):**
- **`App.jsx`**: Main application with AWS Cloudscape UI
- **`CampaignBriefForm.jsx`**: Campaign creation interface
- **`CampaignResults.jsx`**: Real-time status and results display
- **`DownloadsPage.jsx`**: Asset browsing and download interface
- **`MetricsPage.jsx`**: Campaign analytics and metrics

### 2. **Asset Strategy**
- **Primary**: Use existing assets from `/assets` folder as hero images
- **Fallback**: **Single AI-generated hero image using Replicate's Flux model**
- **Campaign Assets**: **AI img2img model enhances hero images** (maintains aspect ratios)
- **Text Overlays**: Python-based text rendering with responsive design

### 3. **AI-Enhanced Asset Generation**
- **Hero Image**: Single base image (existing asset or AI-generated)
- **Img2Img Enhancement**: AI model enhances image quality **maintaining original aspect ratio**
  - **⚠️ Limitation**: All variants have same aspect ratio as hero image
  - **Quality**: AI improves visual appearance and consistency
- **Target Formats**: 1:1 (Instagram/Facebook), 9:16 (Stories/TikTok), 16:9 (YouTube/Covers)

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

### Hero Image Generation (Replicate Flux)
- **Model**: Flux Dev by Black Forest Labs
- **Quality**: Professional product photography with studio lighting
- **Customization**: Generates based on product name and description
- **Usage**: Only when existing assets unavailable (single image, not multiple)
- **API**: Requires Replicate API token from [replicate.com](https://replicate.com/)

### Campaign Asset Generation (Img2Img)
- **Model**: bxclib2/flux_img2img via Replicate
- **Process**: Enhances hero images while maintaining original aspect ratio
- **Quality**: AI-powered visual enhancement and style consistency
- **Parameters**: Configurable denoising (0.25), steps (20), sampling methods
- **⚠️ Limitation**: **Does not change aspect ratios** - maintains hero image dimensions
- **Efficiency**: Single hero image → enhanced campaign assets
- **API**: Uses same Replicate API token

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

3. **Image Generation & Campaign Assets**:
   - **Hero Images**: Single AI-generated image using Replicate's Flux Dev model (when assets unavailable)
   - **Campaign Assets**: AI img2img model enhances images while maintaining hero's aspect ratio
   - **⚠️ Aspect Ratio Limitation**: Img2img model cannot change aspect ratios - all variants match hero dimensions
   - **Professional Quality**: Both hero and enhanced variants produce studio-quality results
   - **Generation Time**: Hero image 10-30 seconds, each img2img enhancement 10-120 seconds
   - **Efficiency**: Single hero → enhanced campaign assets using AI processing
   - Asset reuse prioritized over generation for cost and speed optimization

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
- [x] **GenAI Hero Image Generation**: ✅ **COMPLETED** - Uses Replicate's Flux Dev model for professional image generation
- [x] **AI Campaign Asset Generation**: ✅ **COMPLETED** - Uses img2img model for visual enhancement (maintains aspect ratios)
- [ ] **Data Persistence**: Docker volumes or database integration for data retention
- [x] **AI-Powered Compliance**: ✅ **COMPLETED** - Uses Groq's Llama 3.1 for intelligent content validation
- [ ] **Computer Vision Compliance**: Image analysis for brand guideline validation (basic brand checks removed)
- [ ] **Cloud Storage**: S3/GCS integration with persistent asset management
- [ ] **Database Integration**: PostgreSQL/MongoDB for campaign and metrics storage



## Troubleshooting

### Common Issues

1. **Data Loss After Container Restart**:
   - **Issue**: All generated campaigns, assets, and metrics disappear when containers are recreated
   - **Cause**: No persistent Docker volumes configured
   - **Workaround**: Copy important data out of containers before stopping: `docker cp container_name:/app/backend/output ./backup`

2. **Container Issues**: Ensure Docker and Docker Compose are installed and running

3. **Font Issues**: System falls back to default fonts if custom fonts unavailable


4. **Port Conflicts**: Check that ports 3000 and 8000 are available

5. **AI API Dependencies**:
   - **Issue**: Content moderation or image generation may fail
   - **Cause**: Missing or invalid API keys for Groq/Replicate
   - **Solution**: Ensure valid API keys are configured in `backend/app.py`

6. **Rate Limiting**:
   - **Issue**: AI services may temporarily reject requests
   - **Cause**: Free tier rate limits on Groq or Replicate
   - **Solution**: Wait and retry, or upgrade to paid tiers


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
│   │   ├── creative_generator.py # AI img2img campaign asset generation
│   │   ├── image_generator.py # AI image generation
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

## License

This is a proof-of-concept implementation for demonstration purposes.