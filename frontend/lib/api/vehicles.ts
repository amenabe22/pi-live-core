import { apiClient } from './client';
import type { Vehicle, VehicleStatus } from '../types/api';

export interface VehicleCreate {
  plate_number: string;
  model: string;
  status?: VehicleStatus;
  driver_id?: number | null;
}

export interface VehicleUpdate {
  plate_number?: string;
  model?: string;
  status?: VehicleStatus;
  driver_id?: number | null;
}

export const vehiclesApi = {
  getAll: async (params?: { skip?: number; limit?: number; status_filter?: string }): Promise<Vehicle[]> => {
    const response = await apiClient.get('/vehicles', { params });
    return response.data;
  },

  getById: async (id: number): Promise<Vehicle> => {
    const response = await apiClient.get(`/vehicles/${id}`);
    return response.data;
  },

  create: async (data: VehicleCreate): Promise<Vehicle> => {
    const response = await apiClient.post('/vehicles', data);
    return response.data;
  },

  update: async (id: number, data: VehicleUpdate): Promise<Vehicle> => {
    const response = await apiClient.put(`/vehicles/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/vehicles/${id}`);
  },
};
