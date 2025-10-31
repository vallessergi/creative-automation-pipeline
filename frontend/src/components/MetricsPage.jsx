import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Header, 
  SpaceBetween, 
  Badge, 
  Box,
  StatusIndicator,
  ExpandableSection,
  Alert
} from '@cloudscape-design/components';
import { getAllMetrics } from '../services/api';

export default function MetricsPage({ onError }) {
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAllMetrics();
  }, []);

  const loadAllMetrics = async () => {
    setLoading(true);
    try {
      const result = await getAllMetrics();
      setMetrics(result || []);
    } catch (error) {
      onError(`Error loading metrics: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIndicator = (status) => {
    return status === 'completed' 
      ? <StatusIndicator type="success">Completed</StatusIndicator>
      : <StatusIndicator type="error">Failed</StatusIndicator>;
  };

  const formatDate = (isoString) => {
    try {
      return new Date(isoString).toLocaleString();
    } catch {
      return 'Invalid date';
    }
  };

  if (loading) {
    return (
      <Container>
        <Box>Loading metrics...</Box>
      </Container>
    );
  }

  return (
    <Container
      header={
        <Header 
          variant="h1" 
          description="Analytics and performance metrics for all campaigns"
          actions={
            <Badge color="blue">
              {metrics.length} campaigns tracked
            </Badge>
          }
        >
          Campaign Metrics
        </Header>
      }
    >
      <SpaceBetween direction="vertical" size="l">
        {metrics.length === 0 ? (
          <Alert type="info" statusIconAriaLabel="Info">
            No campaign metrics available yet. Generate campaigns to see analytics here.
          </Alert>
        ) : (
          <SpaceBetween direction="vertical" size="s">
            {metrics.map((metric) => (
              <ExpandableSection
                key={metric.campaign_id}
                headerText={`Campaign ${metric.campaign_id}`}
                variant="container"
                defaultExpanded={false}
                headerActions={
                  <SpaceBetween direction="horizontal" size="s">
                    {getStatusIndicator(metric.final_status)}
                    <Badge color="blue">{metric.summary?.total_products || 0} products</Badge>
                    <Badge color="green">{metric.summary?.total_creatives_generated || 0} images</Badge>
                  </SpaceBetween>
                }
              >
                <SpaceBetween direction="vertical" size="m">
                  <Box>
                    <strong>Created:</strong> {formatDate(metric.timestamp)}
                  </Box>
                  
                  <Box>
                    <strong>Status Reason:</strong> {metric.reason || 'No reason provided'}
                  </Box>
                  
                  <Box>
                    <strong>Target Region:</strong> {metric.campaign_brief?.target_region || 'N/A'}
                  </Box>
                  
                  <Box>
                    <strong>Target Audience:</strong> {metric.campaign_brief?.target_audience || 'N/A'}
                  </Box>
                  
                  <Box>
                    <strong>Campaign Message:</strong> {metric.campaign_brief?.campaign_message || 'N/A'}
                  </Box>

                  <Container header={<Header variant="h3">Products</Header>}>
                    <SpaceBetween direction="vertical" size="s">
                      {metric.campaign_brief?.products?.map((product, index) => (
                        <Box key={index}>
                          <SpaceBetween direction="horizontal" size="s" alignItems="center">
                            <Box>
                              <strong>{product.name}</strong>
                            </Box>
                            {metric.product_metrics?.[product.name] && (
                              <Badge color={metric.product_metrics[product.name].asset_status === 'reused' ? 'green' : 'blue'}>
                                {metric.product_metrics[product.name].asset_status === 'reused' ? 'Assets reused' : 'AI generated'}
                              </Badge>
                            )}
                          </SpaceBetween>
                        </Box>
                      )) || []}
                    </SpaceBetween>
                  </Container>

                  <Container header={<Header variant="h3">Summary</Header>}>
                    <SpaceBetween direction="horizontal" size="l">
                      <Box textAlign="center">
                        <Box fontSize="heading-l" fontWeight="bold">
                          {metric.summary?.products_with_existing_assets || 0}
                        </Box>
                        <Box>Assets Reused</Box>
                      </Box>
                      <Box textAlign="center">
                        <Box fontSize="heading-l" fontWeight="bold">
                          {metric.summary?.products_with_generated_assets || 0}
                        </Box>
                        <Box>AI Generated</Box>
                      </Box>
                      <Box textAlign="center">
                        <Box fontSize="heading-l" fontWeight="bold">
                          {metric.summary?.total_creatives_generated || 0}
                        </Box>
                        <Box>Total Creatives</Box>
                      </Box>
                    </SpaceBetween>
                  </Container>
                </SpaceBetween>
              </ExpandableSection>
            ))}
          </SpaceBetween>
        )}
      </SpaceBetween>
    </Container>
  );
}