# Creative Automation Pipeline

A full-stack automation system for generating social media creative assets, featuring a FastAPI backend and React frontend with AWS Cloudscape Design System.

## Overview

This system automates the creation of social media creatives by:
- Providing a modern web interface for campaign management
- Accepting campaign briefs through forms or JSON API
- Performing content compliance validation before generation
- Reusing existing assets when available
- Creating placeholder images when assets are not available
- Generating multiple aspect ratios (1:1, 9:16, 16:9)
- Adding campaign message overlays with responsive text
- Performing brand compliance checks after generation
- Organizing outputs by product and aspect ratio
- Tracking campaign metrics and performance

## Quick Start

### Prerequisites
- Docker & Docker Compose (required)

### Installation

1. **Run the complete stack**:
```bash
docker-compose up --build
```

The application will be available at:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

## Usage

### Web Interface (Recommended)

1. **Access the frontend** at `http://localhost:3000`
2. **Create Campaign Brief**:
   - Fill out the campaign form with 2+ products
   - Add product names and descriptions
   - Set target region and audience
   - Enter your campaign message
3. **Submit and Monitor**:
   - Click "Generate Campaign"
   - System performs content compliance validation
   - View real-time processing status and logs
   - System performs brand compliance checks after generation
   - Navigate to Downloads tab to access generated assets
4. **View Results**:
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

### Using Existing Assets

Place existing product images in the `assets/` directory:

```
assets/
├── ecoClean_detergent/
│   ├── product_photo1.jpg
│   └── product_photo2.png
└── freshair_fabric_softener/
    └── bottle_image.jpg
```

The system will automatically use these assets instead of generating new ones.

### Check Available Assets

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
| `/assets/info` | GET | Get information about available assets |
| `/metrics` | GET | Get metrics for all campaigns |

## Key Design Decisions

### 1. **Modular Architecture**
**Backend (FastAPI):**
- **`app.py`**: FastAPI server orchestrating the pipeline
- **`asset_manager.py`**: Handles file organization and asset discovery
- **`creative_generator.py`**: Combines images, resizing, and text overlays
- **`image_generator.py`**: Manages placeholder image creation
- **`content_moderator.py`**: Content and brand compliance validation
- **`metrics_manager.py`**: Campaign performance tracking

**Frontend (React):**
- **`App.jsx`**: Main application with AWS Cloudscape UI
- **`CampaignBriefForm.jsx`**: Campaign creation interface
- **`CampaignResults.jsx`**: Real-time status and results display
- **`DownloadsPage.jsx`**: Asset browsing and download interface
- **`MetricsPage.jsx`**: Campaign analytics and metrics

### 2. **Asset Strategy**
- **Primary**: Use existing assets from `/assets` folder
- **Fallback**: Create placeholder images with product names

### 3. **Aspect Ratio Handling**
- **1:1 (1080x1080)**: Instagram posts, Facebook
- **9:16 (1080x1920)**: Instagram stories, TikTok
- **16:9 (1920x1080)**: YouTube, Facebook covers

### 4. **Text Overlay Design**
- Semi-transparent dark overlay at bottom for readability
- Responsive font sizing based on image dimensions
- Word wrapping to prevent text overflow
- Product name at top, campaign message at bottom

### 5. **Compliance Pipeline (Mock Implementation)**
- **Pre-generation**: Basic content validation using static prohibited word lists
- **Post-generation**: Simple brand compliance checks (mock background color validation)
- **Failure Handling**: Campaigns fail safely with detailed logging
- **Metrics Integration**: Compliance failures tracked and reported
- **⚠️ Note**: Current implementation uses static rules for demonstration - production requires LLM/AI-based validation

### 6. **Asynchronous Processing**
- Background tasks for campaign generation
- Non-blocking API responses
- Real-time status tracking with detailed logs
- Comprehensive error handling and recovery

## Assumptions and Limitations

### Assumptions
- **Minimum 2 products** required per campaign
- **English text** support (could be extended for localization)
- **Standard social media dimensions** for aspect ratios
- **JPEG output format** for broad compatibility
- **Ephemeral Usage**: Data persistence not required between container restarts
- **Mock Compliance**: Basic rule-based validation acceptable for proof-of-concept
- **Development Environment**: Not intended for production use without significant enhancements

### Current Limitations

1. **Storage & Data Persistence**:
   - **Ephemeral Storage**: All data (assets, outputs, metrics) disappears when containers are recreated
   - **No Volume Persistence**: Docker volumes not configured for data retention
   - **Local File System Only**: No cloud storage or database integration
   - **Manual Asset Organization**: Assets must be manually placed in backend/assets/

2. **Compliance System (Mock Implementation)**:
   - **Static Rule-Based Checks**: Current content/brand compliance uses hard-coded, simplistic rules
   - **No AI/LLM Integration**: Compliance validation needs sophisticated methods (LLM, computer vision, etc.)
   - **Limited Content Analysis**: Only basic prohibited word filtering
   - **No Brand Intelligence**: Brand compliance checks are superficial mock implementations
   - **Missing Context Awareness**: No understanding of cultural, regional, or industry-specific compliance requirements

3. **Image Generation**:
   - Currently uses placeholder images only
   - Could be extended with GenAI providers (OpenAI DALL-E, Stability AI, Midjourney)
   - Asset reuse prioritized over generation

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
- [ ] **GenAI Image Generation**: Replace placeholder Python image creation with actual GenAI models (DALL-E, Midjourney, Stability AI, etc.) for campaign-specific creative generation
- [ ] **Data Persistence**: Docker volumes or database integration for data retention
- [ ] **AI-Powered Compliance**: LLM-based content validation replacing static rules
- [ ] **Computer Vision Compliance**: Image analysis for brand guideline validation
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

6. **Mock Compliance Behavior**:
   - **Issue**: Campaigns may pass/fail compliance checks unpredictably
   - **Cause**: Static rule implementation for demonstration purposes
   - **Note**: This is expected behavior in the current proof-of-concept

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