import { apiClient } from './client';
import type { Review, DriverStats, ReviewType } from '../types/api';

export interface ReviewCreate {
  travel_id?: string | null;
  driver_id: string;
  rating: number;
  comment?: string | null;
  review_type?: ReviewType;
}

export interface ReviewUpdate {
  rating?: number;
  comment?: string | null;
}

export const reviewsApi = {
  getAll: async (params?: {
    skip?: number;
    limit?: number;
    driver_id?: string;
    travel_id?: string;
    rating?: number;
  }): Promise<Review[]> => {
    const response = await apiClient.get('/reviews', { params });
    return response.data;
  },

  getById: async (id: string): Promise<Review> => {
    const response = await apiClient.get(`/reviews/${id}`);
    return response.data;
  },

  create: async (data: ReviewCreate): Promise<Review> => {
    const response = await apiClient.post('/reviews', data);
    return response.data;
  },

  update: async (id: string, data: ReviewUpdate): Promise<Review> => {
    const response = await apiClient.put(`/reviews/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/reviews/${id}`);
  },

  getDriverStats: async (driverId: string): Promise<DriverStats> => {
    const response = await apiClient.get(`/reviews/driver/${driverId}/stats`);
    return response.data;
  },
};
