const API_BASE = '/api';

// Campaign management
export const submitCampaignBrief = async (campaignBrief) => {
  const response = await fetch(`${API_BASE}/generate-campaign`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(campaignBrief)
  });
  
  if (!response.ok) {
    throw new Error('Failed to submit campaign brief');
  }
  
  return response.json();
};

export const getCampaignStatus = async (campaignId) => {
  const response = await fetch(`${API_BASE}/campaign/${campaignId}`);
  
  if (!response.ok) {
    throw new Error('Failed to get campaign status');
  }
  
  return response.json();
};

export const listCampaigns = async () => {
  const response = await fetch(`${API_BASE}/campaigns`);
  
  if (!response.ok) {
    throw new Error('Failed to list campaigns');
  }
  
  return response.json();
};

// Campaign metrics
export const getAllMetrics = async () => {
  const response = await fetch(`${API_BASE}/metrics`);
  
  if (!response.ok) {
    throw new Error('Failed to get campaign metrics');
  }
  
  return response.json();
};

// Campaign image management
export const getCampaignImages = async (campaignId) => {
  const response = await fetch(`${API_BASE}/campaign/${campaignId}/images`);
  
  if (!response.ok) {
    throw new Error('Failed to get campaign images');
  }
  
  return response.json();
};

export const downloadCampaignImage = (campaignId, productName, filename) => {
  return `${API_BASE}/campaign/${campaignId}/download/${productName}/${filename}`;
};