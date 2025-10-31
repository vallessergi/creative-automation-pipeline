import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import '@cloudscape-design/global-styles/index.css';

// Set theme based on system preference
const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
document.documentElement.setAttribute('data-awsui-theme', isDarkMode ? 'dark' : 'light');

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);