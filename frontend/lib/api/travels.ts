import { apiClient } from './client';
import type { Travel, TravelStatus } from '../types/api';

export interface TravelCreate {
  vehicle_id: number;
  driver_id: number;
  origin_station_id: number;
  destination_station_id: number;
  status?: TravelStatus;
  scheduled_departure?: string | null;
  scheduled_arrival?: string | null;
  distance?: number | null;
  notes?: string | null;
}

export interface TravelUpdate {
  status?: TravelStatus;
  actual_departure?: string | null;
  actual_arrival?: string | null;
  distance?: number | null;
  notes?: string | null;
}

export const travelsApi = {
  getAll: async (params?: {
    skip?: number;
    limit?: number;
    status_filter?: TravelStatus;
    vehicle_id?: number;
    driver_id?: number;
  }): Promise<Travel[]> => {
    const response = await apiClient.get('/travels', { params });
    return response.data;
  },

  getById: async (id: number): Promise<Travel> => {
    const response = await apiClient.get(`/travels/${id}`);
    return response.data;
  },

  create: async (data: TravelCreate): Promise<Travel> => {
    const response = await apiClient.post('/travels', data);
    return response.data;
  },

  update: async (id: number, data: TravelUpdate): Promise<Travel> => {
    const response = await apiClient.put(`/travels/${id}`, data);
    return response.data;
  },

  start: async (id: number): Promise<Travel> => {
    const response = await apiClient.post(`/travels/${id}/start`);
    return response.data;
  },

  complete: async (id: number): Promise<Travel> => {
    const response = await apiClient.post(`/travels/${id}/complete`);
    return response.data;
  },

  cancel: async (id: number): Promise<Travel> => {
    const response = await apiClient.post(`/travels/${id}/cancel`);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/travels/${id}`);
  },
};
