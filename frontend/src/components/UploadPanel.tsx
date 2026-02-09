/**
 * UploadPanel component - File upload interface for shapefiles.
 */

import React, { useState, useRef } from 'react';
import { useAppStore } from '../store/appStore';
import '../styles/UploadPanel.css';

interface UploadPanelProps {
  onClose: () => void;
}

const UploadPanel: React.FC<UploadPanelProps> = ({ onClose }) => {
  const [files, setFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const setUploadStatus = useAppStore((state) => state.setUploadStatus);
  const setCurrentAnalysisId = useAppStore((state) => state.setCurrentAnalysisId);

  const REQUIRED_FILES = ['.shp', '.shx', '.dbf', '.prj'];
  const ARCHIVE_FILES = ['.zip', '.rar'];

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || []);
    setFiles(selectedFiles);
    setError(null);

    // Validate file types
    const fileExtensions = selectedFiles.map((f) => {
      const parts = f.name.split('.');
      return '.' + parts[parts.length - 1].toLowerCase();
    });

    // Check if it's an archive or individual files
    const hasArchive = fileExtensions.some((ext) => ARCHIVE_FILES.includes(ext));
    
    if (hasArchive) {
      // If archive is present, it should contain all required files
      if (selectedFiles.length > 1) {
        setError('Upload either an archive file OR individual shapefile components, not both');
      }
    } else {
      // If individual files, check for required files
      const missingFiles = REQUIRED_FILES.filter(
        (ext) => !fileExtensions.includes(ext)
      );

      if (missingFiles.length > 0) {
        setError(`Missing required files: ${missingFiles.join(', ')}`);
      }
    }
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      setError('Please select files');
      return;
    }

    // Validate file selection
    const fileExtensions = files.map((f) => {
      const parts = f.name.split('.');
      return '.' + parts[parts.length - 1].toLowerCase();
    });

    const hasArchive = fileExtensions.some((ext) => ARCHIVE_FILES.includes(ext));
    
    if (!hasArchive) {
      // If individual files, check for required files
      const missingFiles = REQUIRED_FILES.filter(
        (ext) => !fileExtensions.includes(ext)
      );

      if (missingFiles.length > 0) {
        setError(`Missing required files: ${missingFiles.join(', ')}`);
        return;
      }
    }

    setIsUploading(true);
    setUploadStatus({ status: 'uploading', message: 'Uploading shapefile...' });

    try {
      const formData = new FormData();
      files.forEach((file) => {
        formData.append('files', file);
      });

      const response = await fetch('/api/shapefile/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setUploadStatus({
          status: 'success',
          message: 'Shapefile uploaded successfully',
        });
        setCurrentAnalysisId(data.shapefileId);
        setFiles([]);
        setError(null);

        // Close panel after successful upload
        setTimeout(() => {
          onClose();
        }, 1500);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Upload failed');
        setUploadStatus({
          status: 'error',
          message: errorData.error || 'Upload failed',
        });
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Upload failed';
      setError(errorMessage);
      setUploadStatus({
        status: 'error',
        message: errorMessage,
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.currentTarget.classList.add('drag-over');
  };

  const handleDragLeave = (event: React.DragEvent<HTMLDivElement>) => {
    event.currentTarget.classList.remove('drag-over');
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');

    const droppedFiles = Array.from(event.dataTransfer.files || []);
    setFiles(droppedFiles);
    setError(null);

    // Validate file types
    const fileExtensions = droppedFiles.map((f) => {
      const parts = f.name.split('.');
      return '.' + parts[parts.length - 1].toLowerCase();
    });

    // Check if it's an archive or individual files
    const hasArchive = fileExtensions.some((ext) => ARCHIVE_FILES.includes(ext));
    
    if (hasArchive) {
      // If archive is present, it should contain all required files
      if (droppedFiles.length > 1) {
        setError('Upload either an archive file OR individual shapefile components, not both');
      }
    } else {
      // If individual files, check for required files
      const missingFiles = REQUIRED_FILES.filter(
        (ext) => !fileExtensions.includes(ext)
      );

      if (missingFiles.length > 0) {
        setError(`Missing required files: ${missingFiles.join(', ')}`);
      }
    }
  };

  return (
    <div className="upload-panel">
      <h3>Upload Shapefile</h3>

      {/* Drag and Drop Area */}
      <div
        className="drag-drop-area"
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="drag-drop-content">
          <div className="drag-drop-icon">📁</div>
          <p className="drag-drop-text">
            Drag and drop shapefile or archive here
          </p>
          <p className="drag-drop-subtext">or click to select files (ZIP, RAR, or individual components)</p>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleFileSelect}
          className="file-input"
          accept=".shp,.shx,.dbf,.prj,.zip,.rar"
        />
      </div>

      {/* Required Files Info */}
      <div className="required-files">
        <p className="required-files-label">Upload options:</p>
        <ul className="required-files-list">
          <li>
            <span className="file-icon">📦</span>
            <span>ZIP or RAR archive containing all components</span>
          </li>
          <li>
            <span className="file-icon">📄</span>
            <span>.shp, .shx, .dbf, .prj files individually</span>
          </li>
        </ul>
      </div>

      {/* Selected Files */}
      {files.length > 0 && (
        <div className="selected-files">
          <p className="selected-files-label">Selected files:</p>
          <ul className="selected-files-list">
            {files.map((file) => (
              <li key={file.name}>
                <span className="file-icon">✓</span>
                <span>{file.name}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Error Message */}
      {error && <div className="error-message">{error}</div>}

      {/* Action Buttons */}
      <div className="upload-actions">
        <button
          className="button secondary"
          onClick={onClose}
          disabled={isUploading}
        >
          Cancel
        </button>
        <button
          className="button primary"
          onClick={handleUpload}
          disabled={isUploading || files.length === 0}
        >
          {isUploading ? 'Uploading...' : 'Upload'}
        </button>
      </div>
    </div>
  );
};

export default UploadPanel;
