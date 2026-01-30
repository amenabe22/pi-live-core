import { apiClient } from './client';
import type { LiveTracking, RouteResponse } from '../types/api';

export const trackingApi = {
  getCurrent: async (vehicleId: string): Promise<LiveTracking> => {
    const response = await apiClient.get(`/tracking/vehicle/${vehicleId}/current`);
    return response.data;
  },

  getHistory: async (
    vehicleId: string,
    params?: {
      start_time?: string;
      end_time?: string;
      limit?: number;
    }
  ): Promise<LiveTracking[]> => {
    const response = await apiClient.get(`/tracking/vehicle/${vehicleId}/history`, { params });
    return response.data;
  },

  getRoute: async (
    vehicleId: string,
    params?: {
      travel_id?: string;
      start_time?: string;
      end_time?: string;
    }
  ): Promise<RouteResponse> => {
    const response = await apiClient.get(`/tracking/vehicle/${vehicleId}/route`, { params });
    return response.data;
  },

  create: async (data: {
    vehicle_id: string;
    driver_id: string;
    latitude: number;
    longitude: number;
    speed?: number | null;
    heading?: number | null;
    accuracy?: number | null;
    timestamp: string;
  }): Promise<LiveTracking> => {
    const response = await apiClient.post('/tracking', data);
    return response.data;
  },
};
