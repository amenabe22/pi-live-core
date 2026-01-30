import { apiClient } from './client';
import type { TravelHistory } from '../types/api';

export const historyApi = {
  getTravels: async (params?: {
    skip?: number;
    limit?: number;
    vehicle_id?: string;
    driver_id?: string;
    status_filter?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<TravelHistory[]> => {
    const response = await apiClient.get('/history/travels', { params });
    return response.data;
  },

  getById: async (id: string): Promise<TravelHistory> => {
    const response = await apiClient.get(`/history/travels/${id}`);
    return response.data;
  },

  getByVehicle: async (vehicleId: string, params?: { skip?: number; limit?: number }): Promise<TravelHistory[]> => {
    const response = await apiClient.get(`/history/vehicle/${vehicleId}`, { params });
    return response.data;
  },

  getByDriver: async (driverId: string, params?: { skip?: number; limit?: number }): Promise<TravelHistory[]> => {
    const response = await apiClient.get(`/history/driver/${driverId}`, { params });
    return response.data;
  },
};
