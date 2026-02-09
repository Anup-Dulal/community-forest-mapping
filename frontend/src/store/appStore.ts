/**
 * Zustand store for application state management.
 * Manages upload status, DEM status, analysis status, and map layers.
 */

import { create } from 'zustand';
import {
  UploadStatus,
  DEMStatus,
  AnalysisStatus,
  LayerVisibility,
  MapState,
  AnalysisResult,
} from '../types';

interface AppStore {
  // Status states
  uploadStatus: UploadStatus;
  demStatus: DEMStatus;
  analysisStatus: AnalysisStatus;

  // Map state
  mapState: MapState;

  // Analysis data
  currentAnalysisId: string | null;
  analysisResult: AnalysisResult | null;

  // Actions
  setUploadStatus: (status: UploadStatus) => void;
  setDEMStatus: (status: DEMStatus) => void;
  setAnalysisStatus: (status: AnalysisStatus) => void;
  setMapCenter: (center: [number, number]) => void;
  setMapZoom: (zoom: number) => void;
  setLayerVisibility: (layer: keyof LayerVisibility, visible: boolean) => void;
  setCurrentAnalysisId: (id: string | null) => void;
  setAnalysisResult: (result: AnalysisResult | null) => void;
  resetState: () => void;
}

const initialMapState: MapState = {
  center: [0, 0],
  zoom: 2,
  layers: {
    boundary: true,
    dem: false,
    slope: false,
    aspect: false,
    compartments: false,
    samplePlots: false,
  },
};

export const useAppStore = create<AppStore>((set) => ({
  uploadStatus: { status: 'idle' },
  demStatus: { status: 'idle' },
  analysisStatus: { status: 'idle' },
  mapState: initialMapState,
  currentAnalysisId: null,
  analysisResult: null,

  setUploadStatus: (status: UploadStatus) =>
    set({ uploadStatus: status }),

  setDEMStatus: (status: DEMStatus) =>
    set({ demStatus: status }),

  setAnalysisStatus: (status: AnalysisStatus) =>
    set({ analysisStatus: status }),

  setMapCenter: (center: [number, number]) =>
    set((state) => ({
      mapState: { ...state.mapState, center },
    })),

  setMapZoom: (zoom: number) =>
    set((state) => ({
      mapState: { ...state.mapState, zoom },
    })),

  setLayerVisibility: (layer: keyof LayerVisibility, visible: boolean) =>
    set((state) => ({
      mapState: {
        ...state.mapState,
        layers: {
          ...state.mapState.layers,
          [layer]: visible,
        },
      },
    })),

  setCurrentAnalysisId: (id: string | null) =>
    set({ currentAnalysisId: id }),

  setAnalysisResult: (result: AnalysisResult | null) =>
    set({ analysisResult: result }),

  resetState: () =>
    set({
      uploadStatus: { status: 'idle' },
      demStatus: { status: 'idle' },
      analysisStatus: { status: 'idle' },
      mapState: initialMapState,
      currentAnalysisId: null,
      analysisResult: null,
    }),
}));
