import React, { useState } from 'react';
import {
  Container,
  Header,
  Form,
  FormField,
  Input,
  Textarea,
  Button,
  Box,
  SpaceBetween,
  Alert,
  FileUpload
} from '@cloudscape-design/components';
import { submitCampaignBrief, uploadProductImage } from '../services/api';

export default function CampaignBriefForm({ onCampaignSubmitted, onError }) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    products: [
      { name: '', description: '', image: [] },
      { name: '', description: '', image: [] }
    ],
    target_region: '',
    target_audience: '',
    campaign_message: ''
  });

  const updateProduct = (index, field, value) => {
    const newProducts = [...formData.products];
    newProducts[index][field] = value;
    setFormData({ ...formData, products: newProducts });
  };

  const addProduct = () => {
    setFormData({
      ...formData,
      products: [...formData.products, { name: '', description: '', image: [] }]
    });
  };

  const removeProduct = (index) => {
    if (formData.products.length > 2) {
      const newProducts = formData.products.filter((_, i) => i !== index);
      setFormData({ ...formData, products: newProducts });
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      // First, upload any images for products that have them
      for (const product of formData.products) {
        if (product.image.length > 0 && product.name.trim()) {
          try {
            await uploadProductImage(product.name.trim(), product.image[0]);
          } catch (uploadError) {
            console.warn(`Failed to upload image for product ${product.name}:`, uploadError);
            // Continue with campaign creation even if image upload fails
          }
        }
      }
      
      // Then submit the campaign brief (without the image files)
      const campaignData = {
        ...formData,
        products: formData.products.map(({ name, description }) => ({ name, description }))
      };
      
      const result = await submitCampaignBrief(campaignData);
      onCampaignSubmitted(result);
    } catch (error) {
      onError(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const isValid = formData.products.length >= 2 &&
    formData.products.every(p => p.name.trim() && p.description.trim()) &&
    formData.target_region.trim() &&
    formData.target_audience.trim() &&
    formData.campaign_message.trim();

  return (
    <Container
      header={
        <Header 
          variant="h2" 
          description="Create a campaign brief to generate creative assets"
        >
          Campaign Brief
        </Header>
      }
    >
      <Form
        actions={
          <Button 
            variant="primary" 
            loading={loading}
            disabled={!isValid}
            onClick={handleSubmit}
            iconName="send"
          >
            Generate Campaign
          </Button>
        }
      >
        <SpaceBetween direction="vertical" size="m">
          {/* Products Section */}
          <FormField label="Products" description="At least 2 products are required">
            <SpaceBetween direction="vertical" size="s">
              {formData.products.map((product, index) => (
                <Box key={index}>
                  <SpaceBetween direction="vertical" size="xs">
                    <Header variant="h4" actions={
                      formData.products.length > 2 && (
                        <Button 
                          variant="icon" 
                          iconName="close"
                          onClick={() => removeProduct(index)}
                        />
                      )
                    }>
                      Product {index + 1}
                    </Header>
                    <Input
                      value={product.name}
                      onChange={({ detail }) => updateProduct(index, 'name', detail.value)}
                      placeholder="Product name..."
                    />
                    <Textarea
                      value={product.description}
                      onChange={({ detail }) => updateProduct(index, 'description', detail.value)}
                      placeholder="Product description..."
                      rows={3}
                    />
                    <FormField
                      label="Product Image (Optional)"
                      description="Upload an image for this product (JPG, PNG, WEBP, GIF, BMP)"
                    >
                      <FileUpload
                        onChange={({ detail }) => updateProduct(index, 'image', detail.value)}
                        value={product.image}
                        i18nStrings={{
                          uploadButtonText: e => e ? "Choose files" : "Choose file",
                          dropzoneText: e => e ? "Drop files to upload" : "Drop file to upload",
                          removeFileAriaLabel: e => `Remove file ${e + 1}`,
                          limitShowFewer: "Show fewer files",
                          limitShowMore: "Show more files",
                          errorIconAriaLabel: "Error"
                        }}
                        showFileLastModified
                        showFileSize
                        showFileThumbnail
                        tokenLimit={1}
                        accept="image/*"
                        disabled={loading}
                      />
                    </FormField>
                  </SpaceBetween>
                </Box>
              ))}
              <Button variant="normal" iconName="add-plus" onClick={addProduct}>
                Add Product
              </Button>
            </SpaceBetween>
          </FormField>

          {/* Target Region */}
          <FormField label="Target Region" description="Geographic market for the campaign">
            <Input
              value={formData.target_region}
              onChange={({ detail }) => setFormData({ ...formData, target_region: detail.value })}
              placeholder="e.g., North America, Europe, Asia-Pacific..."
            />
          </FormField>

          {/* Target Audience */}
          <FormField label="Target Audience" description="Demographics and characteristics">
            <Textarea
              value={formData.target_audience}
              onChange={({ detail }) => setFormData({ ...formData, target_audience: detail.value })}
              placeholder="e.g., Environmentally conscious families with children, ages 25-45..."
              rows={3}
            />
          </FormField>

          {/* Campaign Message */}
          <FormField label="Campaign Message" description="Main message to display on creatives">
            <Textarea
              value={formData.campaign_message}
              onChange={({ detail }) => setFormData({ ...formData, campaign_message: detail.value })}
              placeholder="e.g., Clean your family's clothes the natural way..."
              rows={3}
            />
          </FormField>

          {!isValid && (
            <Alert type="warning" statusIconAriaLabel="Warning">
              Please fill in all required fields. At least 2 products are required.
            </Alert>
          )}
        </SpaceBetween>
      </Form>
    </Container>
  );
}