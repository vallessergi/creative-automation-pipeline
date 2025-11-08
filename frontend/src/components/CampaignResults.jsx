import React, { useState, useEffect } from 'react';
import {
  Container,
  Header,
  SpaceBetween,
  Badge,
  Box,
  StatusIndicator,
  ProgressBar,
  ExpandableSection,
  Alert,
  Spinner
} from '@cloudscape-design/components';
import { getCampaignStatus } from '../services/api';

export default function CampaignResults({ campaignId, onError }) {
  const [campaignData, setCampaignData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (campaignId) {
      checkCampaignStatus();
      // Poll for updates if still processing
      const interval = setInterval(() => {
        if (campaignData?.status === 'processing') {
          checkCampaignStatus();
        }
      }, 3000);

      return () => clearInterval(interval);
    }
  }, [campaignId, campaignData?.status]);

  const checkCampaignStatus = async () => {
    setLoading(true);
    try {
      const result = await getCampaignStatus(campaignId);
      setCampaignData(result);
    } catch (error) {
      onError(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (!campaignId) return null;

  const getStatusIndicator = (status) => {
    switch (status) {
      case 'completed':
        return <StatusIndicator type="success">Completed</StatusIndicator>;
      case 'processing':
        return <StatusIndicator type="in-progress">Processing</StatusIndicator>;
      case 'failed':
        return <StatusIndicator type="error">Failed</StatusIndicator>;
      default:
        return <StatusIndicator type="pending">Pending</StatusIndicator>;
    }
  };

  const getProgress = (status) => {
    switch (status) {
      case 'completed': return 100;
      case 'processing': return 60;
      case 'failed': return 100;
      default: return 0;
    }
  };

  return (
    <Container
      header={
        <Header 
          variant="h2" 
          description={`Campaign ID: ${campaignId}`}
          actions={campaignData?.status && getStatusIndicator(campaignData.status)}
        >
          Campaign Results
        </Header>
      }
    >
      <SpaceBetween direction="vertical" size="m">
        {/* Loading Spinner */}
        {loading && (
          <Box textAlign="center" padding="l">
            <SpaceBetween direction="vertical" size="s">
              <Spinner size="large" />
              <Box variant="p" color="text-body-secondary">
                {campaignData?.status === 'processing' ? 'Updating campaign status...' : 'Loading campaign results...'}
              </Box>
            </SpaceBetween>
          </Box>
        )}

        {/* Progress */}
        {campaignData && (
          <Box>
            <ProgressBar
              value={getProgress(campaignData.status)}
              description={campaignData.status === 'processing' ? 'Generating creatives...' : ''}
              variant={campaignData.status === 'failed' ? 'error' : 'success'}
            />
          </Box>
        )}

        {/* Campaign Brief Summary */}
        {campaignData?.brief && (
          <ExpandableSection
            headerText="Campaign Brief"
            variant="container"
            defaultExpanded={false}
          >
            <SpaceBetween direction="vertical" size="s">
              <Box>
                <strong>Products:</strong> {campaignData.brief.products?.length || 0} products
              </Box>
              <Box>
                <strong>Target Region:</strong> {campaignData.brief.target_region}
              </Box>
              <Box>
                <strong>Target Audience:</strong> {campaignData.brief.target_audience}
              </Box>
              <Box>
                <strong>Campaign Message:</strong> {campaignData.brief.campaign_message}
              </Box>
            </SpaceBetween>
          </ExpandableSection>
        )}

        {/* Processing Logs */}
        {campaignData?.logs && (
          <ExpandableSection
            headerText="Processing Logs"
            variant="container"
            defaultExpanded={false}
          >
            <Box>
              <ul style={{ margin: 0, paddingLeft: '20px' }}>
                {campaignData.logs.map((log, index) => (
                  <li key={index} style={{ marginBottom: '4px' }}>
                    {log}
                  </li>
                ))}
              </ul>
            </Box>
          </ExpandableSection>
        )}

        {/* Error State */}
        {campaignData?.status === 'failed' && (
          <Alert type="error" statusIconAriaLabel="Error">
            Campaign generation failed. Check processing logs for details.
          </Alert>
        )}

        {/* Success State */}
        {campaignData?.status === 'completed' && (
          <Alert type="success" statusIconAriaLabel="Success">
            Campaign completed successfully! Check the output/{campaignId}/ folder for your creative assets.
          </Alert>
        )}
      </SpaceBetween>
    </Container>
  );
}