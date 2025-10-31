import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Header, 
  SpaceBetween, 
  Select,
  Badge, 
  Box,
  Button,
  ExpandableSection,
  Alert
} from '@cloudscape-design/components';
import { listCampaigns, getCampaignImages, downloadCampaignImage } from '../services/api';

export default function DownloadsPage({ onError }) {
  const [campaigns, setCampaigns] = useState([]);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [imageData, setImageData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAvailableCampaigns();
  }, []);

  useEffect(() => {
    if (selectedCampaign) {
      loadCampaignImages();
    }
  }, [selectedCampaign]);

  const loadAvailableCampaigns = async () => {
    try {
      const campaignIds = await listCampaigns();
      const campaignOptions = campaignIds.map(id => ({
        label: `Campaign ${id}`,
        value: id
      }));
      setCampaigns(campaignOptions);
    } catch (error) {
      onError(`Error loading campaigns: ${error.message}`);
    }
  };

  const loadCampaignImages = async () => {
    if (!selectedCampaign) return;
    
    setLoading(true);
    try {
      const result = await getCampaignImages(selectedCampaign.value);
      setImageData(result);
    } catch (error) {
      onError(`Error loading images: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = (productName, filename) => {
    const downloadUrl = downloadCampaignImage(selectedCampaign.value, productName, filename);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Container
      header={
        <Header 
          variant="h1" 
          description="Browse and download generated campaign images"
        >
          Download Center
        </Header>
      }
    >
      <SpaceBetween direction="vertical" size="l">
        <Container
          header={<Header variant="h2">Select Campaign</Header>}
        >
          <SpaceBetween direction="vertical" size="s">
            <Select
              selectedOption={selectedCampaign}
              onChange={({ detail }) => setSelectedCampaign(detail.selectedOption)}
              options={campaigns}
              placeholder="Choose a campaign..."
              loadingText="Loading campaigns..."
              statusType={campaigns.length === 0 ? "loading" : "finished"}
            />
            
            {campaigns.length === 0 && (
              <Alert type="info" statusIconAriaLabel="Info">
                No campaigns found. Generate a campaign first to see download options.
              </Alert>
            )}
          </SpaceBetween>
        </Container>

        {imageData && (
          <Container
            header={
              <Header 
                variant="h2" 
                description={`Campaign: ${imageData.campaign_id}`}
                actions={
                  <Badge color="green">
                    {imageData.total_images} Images
                  </Badge>
                }
              >
                Campaign Images
              </Header>
            }
          >
            <SpaceBetween direction="vertical" size="s">
              {Object.entries(imageData.images).map(([productName, images]) => (
                <ExpandableSection
                  key={productName}
                  headerText={productName}
                  variant="container"
                  defaultExpanded={true}
                  headerActions={
                    <Badge color="blue">
                      {images.length} formats
                    </Badge>
                  }
                >
                  <SpaceBetween direction="vertical" size="xs">
                    {images.map((image, index) => (
                      <Box key={index}>
                        <SpaceBetween direction="horizontal" size="s" alignItems="center">
                          <Box>
                            <strong>{image.aspect_ratio}</strong> ({image.aspect_ratio === '1:1' ? 'Square' : image.aspect_ratio === '9:16' ? 'Portrait' : 'Landscape'})
                          </Box>
                          <Badge color="grey">
                            {(image.size / 1024).toFixed(1)} KB
                          </Badge>
                          <Button
                            variant="primary"
                            size="small"
                            iconName="download"
                            onClick={() => handleDownload(productName, image.filename)}
                          >
                            Download
                          </Button>
                        </SpaceBetween>
                      </Box>
                    ))}
                  </SpaceBetween>
                </ExpandableSection>
              ))}
            </SpaceBetween>
          </Container>
        )}
      </SpaceBetween>
    </Container>
  );
}