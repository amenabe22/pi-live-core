import { apiClient } from './client';
import type { Station, VehicleAtStationCheck } from '../types/api';

export interface StationCreate {
  name: string;
  latitude: number;
  longitude: number;
  radius?: number;
  address?: string | null;
}

export interface StationUpdate {
  name?: string;
  latitude?: number;
  longitude?: number;
  radius?: number;
  address?: string | null;
}

export const stationsApi = {
  getAll: async (params?: { skip?: number; limit?: number }): Promise<Station[]> => {
    const response = await apiClient.get('/stations', { params });
    return response.data;
  },

  getById: async (id: string): Promise<Station> => {
    const response = await apiClient.get(`/stations/${id}`);
    return response.data;
  },

  create: async (data: StationCreate): Promise<Station> => {
    const response = await apiClient.post('/stations', data);
    return response.data;
  },

  update: async (id: string, data: StationUpdate): Promise<Station> => {
    const response = await apiClient.put(`/stations/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/stations/${id}`);
  },

  checkVehicleAtStation: async (vehicleId: string): Promise<VehicleAtStationCheck> => {
    const response = await apiClient.get(`/stations/check/${vehicleId}/at-station`);
    return response.data;
  },
};
