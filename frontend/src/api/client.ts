import { Batch, Hub, Reading, TokenResponse, User } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    const token = localStorage.getItem('bt_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = { ...this.getHeaders(), ...options.headers };

    const response = await fetch(url, { ...options, headers });
    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem('bt_token');
        localStorage.removeItem('bt_user');
      }
      let errorMsg = `API Error: ${response.status} ${response.statusText}`;
      try {
        const errorJson = await response.json();
        if (errorJson.detail) {
          errorMsg = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
        }
      } catch {
        // use default error message
      }
      throw new Error(errorMsg);
    }
    return response.json();
  }

  // Auth
  async login(formData: FormData): Promise<TokenResponse> {
    const url = `${API_BASE_URL}/api/v1/auth/login`;
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) {
      throw new Error('Invalid credentials');
    }
    return response.json();
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/api/v1/auth/me');
  }

  // Hubs
  async getHubs(): Promise<Hub[]> {
    return this.request<Hub[]>('/api/v1/hubs/');
  }

  // Batches
  async getBatches(status?: string, hubId?: string): Promise<Batch[]> {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (hubId) params.append('hub_id', hubId);
    const qs = params.toString() ? `?${params.toString()}` : '';
    return this.request<Batch[]>(`/api/v1/batches/${qs}`);
  }

  async getBatch(id: string): Promise<Batch> {
    return this.request<Batch>(`/api/v1/batches/${id}`);
  }

  async createBatch(data: {
    hub_id: string;
    crop_type: string;
    initial_weight_kg: number;
    target_moisture_pct?: number;
  }): Promise<Batch> {
    return this.request<Batch>('/api/v1/batches/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateBatch(id: string, data: Partial<Batch>): Promise<Batch> {
    return this.request<Batch>(`/api/v1/batches/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  // Readings
  async getBatchReadings(batchId: string): Promise<Reading[]> {
    return this.request<Reading[]>(`/api/v1/readings/?batch_id=${batchId}`);
  }
}

export const api = new ApiClient();

