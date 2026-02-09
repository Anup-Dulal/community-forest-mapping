import React from 'react';
import './App.css';
import DashboardLayout from './components/DashboardLayout';

/**
 * Main App component for Community Forest Mapping system.
 * Serves as the root component for the React application.
 */
function App() {
  return (
    <div className="app">
      <DashboardLayout />
    </div>
  );
}

export default App;
