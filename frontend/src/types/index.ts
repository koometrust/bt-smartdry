export type UserRole = 'operator' | 'administrator';
export type QualityGrade = 'export' | 'standard' | 'downgraded';
export type BatchStatus = 'active' | 'completed';
export type CropType = 'moringa' | 'hibiscus' | 'prunus';
export type HubLocation = 'meru' | 'tharaka_nithi' | 'eldoret';

export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  role: UserRole;
  hub_id?: string;
  phone_number?: string;
  preferred_language: 'en' | 'sw';
}

export interface Hub {
  id: string;
  name: string;
  location: string;
  total_capacity_kg: number;
}

export interface Batch {
  id: string;
  hub_id: string;
  crop_type: string;
  initial_weight_kg: number;
  target_moisture_pct: number;
  current_moisture_pct?: number;
  status: BatchStatus;
  predicted_remaining_hours?: number;
  predicted_quality_grade?: QualityGrade;
  current_advisory_en?: string;
  current_advisory_sw?: string;
  start_time: string;
  end_time?: string;
  final_quality_grade?: QualityGrade;
  created_by_user_id?: string;
}

export interface Reading {
  id: string;
  batch_id: string;
  temperature: number;
  humidity: number;
  vpd: number;
  current_moisture: number;
  ambient_temperature: number;
  ambient_humidity: number;
  timestamp: string;
}

export interface Alert {
  id: string;
  batch_id: string;
  alert_type: string;
  channel: string;
  message: string;
  phone_number: string;
  status: string;
  sent_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

