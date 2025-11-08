import React, { useState } from 'react';
import { 
  Header, 
  AppLayout, 
  ContentLayout, 
  SpaceBetween,
  Flashbar,
  TopNavigation,
  Container,
  Tabs
} from '@cloudscape-design/components';
import { CampaignBriefForm, CampaignResults, DownloadsPage, MetricsPage, UploadForm } from './components';

export default function App() {
  const [currentCampaignId, setCurrentCampaignId] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [activeTab, setActiveTab] = useState('upload');

  const addNotification = (message, type = 'success') => {
    const id = Date.now().toString();
    setNotifications(prev => [...prev, { id, message, type }]);
  };

  const dismissNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const handleCampaignSubmitted = (result) => {
    setCurrentCampaignId(result.campaign_id);
    addNotification(result.message, 'success');
  };

  const handleError = (message) => {
    addNotification(message, 'error');
  };

  const tabs = [
    {
      id: 'upload',
      label: 'Upload Assets',
      content: (
        <UploadForm
          onError={handleError}
          onSuccess={(message) => addNotification(message, 'success')}
        />
      )
    },
    {
      id: 'create',
      label: 'Create Campaign',
      content: (
        <SpaceBetween direction="vertical" size="l">
          <CampaignBriefForm
            onCampaignSubmitted={handleCampaignSubmitted}
            onError={handleError}
          />
          <CampaignResults
            campaignId={currentCampaignId}
            onError={handleError}
          />
        </SpaceBetween>
      )
    },
    {
      id: 'downloads',
      label: 'Downloads',
      content: (
        <DownloadsPage
          onError={handleError}
        />
      )
    },
    {
      id: 'metrics',
      label: 'Metrics',
      content: (
        <MetricsPage
          onError={handleError}
        />
      )
    }
  ];

  return (
    <>
      <TopNavigation
        identity={{
          href: "#",
          title: "Creative Automation Pipeline",
          logo: { src: "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDJMMTMgOUwyMCA5TDE1IDE0TDE3IDIxTDEwIDEzTDMgMjFMNSAxNEwwIDlMNyA5TDEwIDJaIiBmaWxsPSJjdXJyZW50Q29sb3IiLz4KPHN2Zz4K", alt: "Creative" }
        }}
        utilities={[
          {
            type: "button",
            text: window.matchMedia('(prefers-color-scheme: dark)').matches ? "Dark" : "Light",
            title: `${window.matchMedia('(prefers-color-scheme: dark)').matches ? 'Dark' : 'Light'} mode`
          }
        ]}
      />
      
      <AppLayout
        navigationHide
        toolsHide
        content={
          <ContentLayout
            defaultPadding
            header={
              <Header 
                variant="h1"
                description="Automate creative asset generation for social media campaigns using GenAI"
              >
                Creative Automation Pipeline
              </Header>
            }
          >
            <Container>
              <SpaceBetween direction="vertical" size="l">
                <Flashbar 
                  items={notifications.map(({ id, message, type }) => ({
                    id,
                    content: message,
                    type,
                    dismissible: true,
                    onDismiss: () => dismissNotification(id)
                  }))}
                />
                
                <Tabs
                  activeTabId={activeTab}
                  onChange={({ detail }) => setActiveTab(detail.activeTabId)}
                  tabs={tabs}
                />
              </SpaceBetween>
            </Container>
          </ContentLayout>
        }
      />
    </>
  );
}