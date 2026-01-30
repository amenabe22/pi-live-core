// API Types matching backend schemas

export type UserRole = 'driver' | 'user' | 'admin';
export type VehicleStatus = 'active' | 'inactive' | 'maintenance';
export type TravelStatus = 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
export type ReviewType = 'driver' | 'trip' | 'service';
export type HistoryStatus = 'completed' | 'cancelled';

export interface User {
  id: number;
  email: string;
  role: UserRole;
  created_at: string;
}

export interface Vehicle {
  id: number;
  plate_number: string;
  model: string;
  status: VehicleStatus;
  driver_id: number | null;
  created_at: string;
  driver?: User;
}

export interface Station {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  radius: number;
  address: string | null;
  created_at: string;
}

export interface Travel {
  id: number;
  vehicle_id: number;
  driver_id: number;
  origin_station_id: number;
  destination_station_id: number;
  status: TravelStatus;
  scheduled_departure: string | null;
  actual_departure: string | null;
  scheduled_arrival: string | null;
  actual_arrival: string | null;
  distance: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  vehicle?: Vehicle;
  driver?: User;
  origin_station?: Station;
  destination_station?: Station;
}

export interface TravelHistory {
  id: number;
  travel_id: number;
  vehicle_id: number;
  driver_id: number;
  origin_station_id: number;
  destination_station_id: number;
  departure_time: string;
  arrival_time: string | null;
  distance_km: number | null;
  duration_minutes: number | null;
  status: HistoryStatus;
  created_at: string;
}

export interface Review {
  id: number;
  travel_id: number | null;
  driver_id: number;
  reviewer_id: number;
  rating: number;
  comment: string | null;
  review_type: ReviewType;
  created_at: string;
  updated_at: string;
  driver?: User;
  reviewer?: User;
}

export interface LiveTracking {
  id: number;
  vehicle_id: number;
  driver_id: number;
  latitude: number;
  longitude: number;
  speed: number | null;
  heading: number | null;
  accuracy: number | null;
  timestamp: string;
  created_at: string;
}

export interface LocationUpdate {
  latitude: number;
  longitude: number;
  timestamp?: string;
  speed?: number;
  heading?: number;
  accuracy?: number;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  role?: UserRole;
}

export interface VehicleAtStationCheck {
  vehicle_id: number;
  is_at_station: boolean;
  station_id: number | null;
  station_name: string | null;
  distance_meters: number | null;
}

export interface RoutePoint {
  latitude: number;
  longitude: number;
  timestamp: string;
  speed: number | null;
}

export interface RouteResponse {
  vehicle_id: number;
  travel_id: number | null;
  points: RoutePoint[];
  total_points: number;
  start_time: string;
  end_time: string;
}

export interface DriverStats {
  driver_id: number;
  average_rating: number;
  total_reviews: number;
  rating_breakdown: Record<number, number>;
}
