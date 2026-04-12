import React from 'react';
import '../styles/WelcomeScreen.css';

/**
 * WelcomeScreen Component
 * Displays welcome screen with step-by-step instructions.
 * Requirements: 20.1, 20.6
 */

interface WelcomeScreenProps {
  onStart: () => void;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onStart }) => {
  return (
    <div className="welcome-screen">
      <div className="welcome-container">
        <div className="welcome-header">
          <h1>Community Forest Mapping</h1>
          <p className="subtitle">Analyze your forest boundary with ease</p>
        </div>

        <div className="welcome-content">
          <div className="welcome-intro">
            <p>
              Welcome to the Community Forest Mapping application. This tool helps you analyze
              forest boundaries, generate compartments, and calculate terrain characteristics.
            </p>
          </div>

          <div className="workflow-steps-guide">
            <h2>How It Works</h2>
            <div className="steps-list">
              <div className="step-guide">
                <div className="step-number">1</div>
                <div className="step-content">
                  <h3>Upload Boundary</h3>
                  <p>Upload your community forest boundary as a shapefile (.shp, .shx, .dbf, .prj)</p>
                </div>
              </div>

              <div className="step-guide">
                <div className="step-number">2</div>
                <div className="step-content">
                  <h3>Verify Boundary</h3>
                  <p>Review the uploaded boundary on the interactive map and verify it's correct</p>
                </div>
              </div>

              <div className="step-guide">
                <div className="step-number">3</div>
                <div className="step-content">
                  <h3>Generate Compartments</h3>
                  <p>Automatically divide the forest into equal-area compartments for inventory</p>
                </div>
              </div>

              <div className="step-guide">
                <div className="step-number">4</div>
                <div className="step-content">
                  <h3>Calculate Terrain</h3>
                  <p>Analyze slope and aspect to understand terrain characteristics</p>
                </div>
              </div>

              <div className="step-guide">
                <div className="step-number">5</div>
                <div className="step-content">
                  <h3>Export Results</h3>
                  <p>Download maps and data in PDF, PNG, or CSV format for field use</p>
                </div>
              </div>
            </div>
          </div>

          <div className="welcome-features">
            <h2>Key Features</h2>
            <ul className="features-list">
              <li>
                <span className="feature-icon">📍</span>
                <span>Real-time map visualization with satellite imagery</span>
              </li>
              <li>
                <span className="feature-icon">⚡</span>
                <span>Live progress updates for all calculations</span>
              </li>
              <li>
                <span className="feature-icon">📊</span>
                <span>Detailed statistics and distribution analysis</span>
              </li>
              <li>
                <span className="feature-icon">📱</span>
                <span>Mobile-friendly responsive design</span>
              </li>
              <li>
                <span className="feature-icon">💾</span>
                <span>Offline caching for field work</span>
              </li>
              <li>
                <span className="feature-icon">🔄</span>
                <span>Automatic retry with error recovery</span>
              </li>
            </ul>
          </div>

          <div className="welcome-requirements">
            <h2>What You'll Need</h2>
            <ul className="requirements-list">
              <li>A shapefile of your community forest boundary</li>
              <li>Internet connection for satellite imagery and elevation data</li>
              <li>A modern web browser (Chrome, Firefox, Safari, or Edge)</li>
            </ul>
          </div>

          <div className="welcome-tips">
            <h2>Tips for Best Results</h2>
            <ul className="tips-list">
              <li>Ensure your shapefile is in a recognized coordinate system</li>
              <li>Verify the boundary area is between 0.1 and 100,000 sq km</li>
              <li>Use a stable internet connection for data downloads</li>
              <li>Allow time for satellite imagery and elevation data to load</li>
              <li>Review the preview before exporting final maps</li>
            </ul>
          </div>
        </div>

        <div className="welcome-footer">
          <button className="btn btn-primary btn-large" onClick={onStart}>
            Get Started →
          </button>
          <p className="welcome-note">
            This workflow will guide you through each step. You can navigate back and forth as needed.
          </p>
        </div>
      </div>
    </div>
  );
};
