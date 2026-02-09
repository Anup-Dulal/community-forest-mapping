import axios from 'axios';

const API_BASE_URL = import.meta.env.REACT_APP_API_URL || 'http://localhost:8080/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

/**
 * Shapefile API endpoints
 */
export const shapefileAPI = {
  upload: (files: File[]) => {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    return apiClient.post('/shapefile/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getById: (id: string) => apiClient.get(`/shapefile/${id}`),
};

/**
 * DEM API endpoints
 */
export const demAPI = {
  download: (shapefileId: string) =>
    apiClient.post('/dem/download', { shapefileId }),
  getStatus: (demId: string) => apiClient.get(`/dem/${demId}/status`),
};

/**
 * Map generation API endpoints
 */
export const mapAPI = {
  generate: (shapefileId: string, params: any) =>
    apiClient.post('/maps/generate', { shapefileId, ...params }),
  getSlope: (analysisId: string) => apiClient.get(`/maps/${analysisId}/slope`),
  getAspect: (analysisId: string) => apiClient.get(`/maps/${analysisId}/aspect`),
  getCompartments: (analysisId: string) =>
    apiClient.get(`/maps/${analysisId}/compartments`),
  getSamplePlots: (analysisId: string) =>
    apiClient.get(`/maps/${analysisId}/sample-plots`),
};

/**
 * Export API endpoints
 */
export const exportAPI = {
  exportCoordinatesCSV: (analysisId: string) =>
    apiClient.get(`/export/${analysisId}/coordinates/csv`, {
      responseType: 'blob',
    }),
  exportCoordinatesExcel: (analysisId: string) =>
    apiClient.get(`/export/${analysisId}/coordinates/excel`, {
      responseType: 'blob',
    }),
  exportMapPDF: (analysisId: string) =>
    apiClient.get(`/export/${analysisId}/map/pdf`, { responseType: 'blob' }),
  exportMapPNG: (analysisId: string) =>
    apiClient.get(`/export/${analysisId}/map/png`, { responseType: 'blob' }),
};

export default apiClient;
