// API Types matching backend schemas

export type UserRole = 'driver' | 'user' | 'admin';
export type VehicleStatus = 'active' | 'inactive' | 'maintenance';
export type TravelStatus = 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
export type ReviewType = 'driver' | 'trip' | 'service';
export type HistoryStatus = 'completed' | 'cancelled';

export interface User {
  id: string;
  email: string;
  role: UserRole;
  created_at: string;
}

export interface Vehicle {
  id: string;
  plate_number: string;
  model: string;
  status: VehicleStatus;
  driver_id: string | null;
  created_at: string;
  driver?: User;
}

export interface Station {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  radius: number;
  address: string | null;
  created_at: string;
}

export interface Travel {
  id: string;
  vehicle_id: string;
  driver_id: string;
  origin_station_id: string;
  destination_station_id: string;
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
  id: string;
  travel_id: string;
  vehicle_id: string;
  driver_id: string;
  origin_station_id: string;
  destination_station_id: string;
  departure_time: string;
  arrival_time: string | null;
  distance_km: number | null;
  duration_minutes: number | null;
  status: HistoryStatus;
  created_at: string;
}

export interface Review {
  id: string;
  travel_id: string | null;
  driver_id: string;
  reviewer_id: string;
  rating: number;
  comment: string | null;
  review_type: ReviewType;
  created_at: string;
  updated_at: string;
  driver?: User;
  reviewer?: User;
}

export interface LiveTracking {
  id: string;
  vehicle_id: string;
  driver_id: string;
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
  vehicle_id: string;
  is_at_station: boolean;
  station_id: string | null;
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
  vehicle_id: string;
  travel_id: string | null;
  points: RoutePoint[];
  total_points: number;
  start_time: string;
  end_time: string;
}

export interface DriverStats {
  driver_id: string;
  average_rating: number;
  total_reviews: number;
  rating_breakdown: Record<number, number>;
}
