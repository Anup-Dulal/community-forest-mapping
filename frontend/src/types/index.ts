/**
 * Type definitions for Community Forest Mapping system.
 */

export interface UploadStatus {
  status: 'idle' | 'uploading' | 'success' | 'error';
  message?: string;
  progress?: number;
}

export interface DEMStatus {
  status: 'idle' | 'downloading' | 'clipping' | 'complete' | 'error';
  message?: string;
  progress?: number;
  source?: string;
}

export interface AnalysisStatus {
  status: 'idle' | 'processing' | 'complete' | 'error';
  message?: string;
  progress?: number;
}

export interface LayerVisibility {
  boundary: boolean;
  dem: boolean;
  slope: boolean;
  aspect: boolean;
  compartments: boolean;
  samplePlots: boolean;
}

export interface MapState {
  center: [number, number];
  zoom: number;
  layers: LayerVisibility;
}

export interface AnalysisResult {
  id: string;
  shapefileId: string;
  demId?: string;
  slopeRasterPath?: string;
  aspectRasterPath?: string;
  compartmentGeometryPath?: string;
  samplePlotGeometryPath?: string;
  status: 'pending' | 'processing' | 'complete' | 'error';
  generatedAt?: string;
}

export interface SamplePlot {
  id: string;
  plotId: string;
  compartmentId: string;
  easting: number;
  northing: number;
  latitude: number;
  longitude: number;
}

export interface ExportOptions {
  format: 'csv' | 'excel' | 'pdf' | 'png';
  mapType?: 'slope' | 'aspect' | 'compartment' | 'sample_plots';
}
