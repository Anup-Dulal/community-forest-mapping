import axios from 'axios';

const API_BASE_URL = '/api';

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
    console.log('Uploading to:', apiClient.defaults.baseURL);
    return apiClient.post('/shapefile/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).catch(err => {
      console.error('Upload error:', err.response?.status, err.response?.data);
      throw err;
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
 * Compartment API endpoints
 */
export interface CompartmentSpec {
  compartmentNumber: number;
  subCompartmentCount: number;
}

export interface HierarchicalCompartmentRequest {
  boundaryWkt: string;
  analysisId: string;
  compartments: CompartmentSpec[];
}

export const compartmentAPI = {
  /**
   * Generate flat compartments (legacy)
   */
  generate: (shapefileId: string, numCompartments: number) =>
    apiClient.post('/compartments/generate', null, {
      params: { shapefileId, numCompartments },
    }),

  /**
   * Generate hierarchical compartments with sub-compartments
   */
  generateHierarchical: (request: HierarchicalCompartmentRequest) =>
    apiClient.post('/compartments/generate-hierarchical', request),

  /**
   * Get compartments for an analysis
   */
  getByAnalysisId: (analysisId: string) =>
    apiClient.get(`/compartments/analysis/${analysisId}`),

  /**
   * Get analysis details
   */
  getAnalysisDetails: (analysisId: string) =>
    apiClient.get(`/compartments/${analysisId}/details`),
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
