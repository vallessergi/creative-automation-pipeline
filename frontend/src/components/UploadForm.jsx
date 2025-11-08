import React, { useState } from 'react';
import {
  Container,
  Header,
  SpaceBetween,
  FormField,
  Input,
  FileUpload,
  Button,
  Box,
  Alert,
  StatusIndicator
} from '@cloudscape-design/components';
import { uploadProductImage } from '../services/api';

export default function UploadForm({ onError, onSuccess }) {
  const [productName, setProductName] = useState('');
  const [selectedFile, setSelectedFile] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);

  const handleSubmit = async () => {
    if (!productName.trim()) {
      onError('Product name is required');
      return;
    }

    if (!selectedFile.length) {
      onError('Please select an image file');
      return;
    }

    setLoading(true);
    setUploadResult(null);

    try {
      const result = await uploadProductImage(productName.trim(), selectedFile[0]);
      setUploadResult(result);
      onSuccess?.(result.message);
      
      // Reset form
      setProductName('');
      setSelectedFile([]);
    } catch (error) {
      onError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = ({ detail }) => {
    setSelectedFile(detail.value);
    setUploadResult(null);
  };

  const isFormValid = productName.trim() && selectedFile.length > 0;

  return (
    <Container
      header={
        <Header
          variant="h2"
          description="Upload product images that will be used in campaign generation"
        >
          Upload Product Images
        </Header>
      }
    >
      <SpaceBetween direction="vertical" size="l">
        <FormField
          label="Product Name"
          description="Enter the name of the product for this image"
        >
          <Input
            value={productName}
            onChange={({ detail }) => setProductName(detail.value)}
            placeholder="e.g., coca_cola, water, etc."
            disabled={loading}
          />
        </FormField>

        <FormField
          label="Product Image"
          description="Select an image file (JPG, PNG, WEBP, GIF, BMP)"
        >
          <FileUpload
            onChange={handleFileChange}
            value={selectedFile}
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

        <Box>
          <Button
            variant="primary"
            onClick={handleSubmit}
            loading={loading}
            disabled={!isFormValid}
          >
            Upload Image
          </Button>
        </Box>

        {uploadResult && (
          <Alert
            statusIconAriaLabel="Success"
            type="success"
            header="Upload Successful"
          >
            <SpaceBetween direction="vertical" size="s">
              <Box>
                <strong>Product:</strong> {uploadResult.product_name}
              </Box>
              <Box>
                <strong>File:</strong> {uploadResult.file_info.filename} 
                ({Math.round(uploadResult.file_info.size / 1024)} KB)
              </Box>
              <Box>
                <strong>Stored in:</strong> {uploadResult.asset_directory}
              </Box>
              <Box variant="small" color="text-status-success">
                <StatusIndicator type="success">
                  Image ready for use in campaigns
                </StatusIndicator>
              </Box>
            </SpaceBetween>
          </Alert>
        )}
      </SpaceBetween>
    </Container>
  );
}