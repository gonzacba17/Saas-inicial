import { AuthResponse, LoginRequest, RegisterRequest, User } from '../types/auth';
import { Business, BusinessCreate, Product, ProductCreate } from '../types/business';
import { Order, OrderCreate, OrderUpdate, OrderStatus } from '../types/order';
import { BusinessAnalytics, DateRangeStats, DailySales } from '../types/analytics';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = localStorage.getItem('access_token');
    const url = `${this.baseURL}${endpoint}`;

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      // Handle specific HTTP status codes
      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        let errorData: any = null;

        try {
          errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
          // If response is not JSON, use status text
          errorMessage = response.statusText || errorMessage;
        }

        // Create specific error types for better frontend handling
        const error = new Error(errorMessage) as any;
        error.status = response.status;
        error.statusText = response.statusText;
        error.data = errorData;

        // Handle specific status codes
        switch (response.status) {
          case 401:
            // Unauthorized - clear token and redirect to login
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_id');
            localStorage.removeItem('role');
            error.type = 'UNAUTHORIZED';
            break;
          case 403:
            // Forbidden - user doesn't have permission
            error.type = 'FORBIDDEN';
            break;
          case 404:
            // Not Found
            error.type = 'NOT_FOUND';
            break;
          case 422:
            // Validation Error
            error.type = 'VALIDATION_ERROR';
            break;
          case 500:
            // Internal Server Error
            error.type = 'SERVER_ERROR';
            break;
          default:
            error.type = 'UNKNOWN_ERROR';
        }

        throw error;
      }

      return response.json();
    } catch (error: any) {
      // Network error or other fetch failures
      if (!error.status) {
        error.type = 'NETWORK_ERROR';
        error.message = 'Network error - please check your connection';
      }
      throw error;
    }
  }

  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    try {
      const response = await fetch(`${this.baseURL}/api/v1/auth/login`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        let errorMessage = 'Login failed';
        let errorData: any = null;

        try {
          errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
          errorMessage = response.statusText || errorMessage;
        }

        const error = new Error(errorMessage) as any;
        error.status = response.status;
        error.statusText = response.statusText;
        error.data = errorData;

        switch (response.status) {
          case 401:
            error.type = 'INVALID_CREDENTIALS';
            break;
          case 422:
            error.type = 'VALIDATION_ERROR';
            break;
          case 500:
            error.type = 'SERVER_ERROR';
            break;
          default:
            error.type = 'LOGIN_ERROR';
        }

        throw error;
      }

      return response.json();
    } catch (error: any) {
      if (!error.status) {
        error.type = 'NETWORK_ERROR';
        error.message = 'Network error - please check your connection';
      }
      throw error;
    }
  }

  async register(userData: RegisterRequest): Promise<User> {
    return this.request<User>('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/api/v1/auth/me');
  }

  // Business methods
  async getBusinesses(): Promise<Business[]> {
    return this.request<Business[]>('/api/v1/businesses');
  }

  async getBusiness(id: string): Promise<Business> {
    return this.request<Business>(`/api/v1/businesses/${id}`);
  }

  async createBusiness(business: BusinessCreate): Promise<Business> {
    return this.request<Business>('/api/v1/businesses', {
      method: 'POST',
      body: JSON.stringify(business),
    });
  }

  // Product methods
  async getProducts(params?: { business_id?: string; category?: string; is_available?: boolean }): Promise<Product[]> {
    const searchParams = new URLSearchParams();
    if (params?.business_id) searchParams.append('business_id', params.business_id);
    if (params?.category) searchParams.append('category', params.category);
    if (params?.is_available !== undefined) searchParams.append('is_available', params.is_available.toString());
    
    const query = searchParams.toString();
    return this.request<Product[]>(`/api/v1/products${query ? `?${query}` : ''}`);
  }

  async getBusinessProducts(businessId: string): Promise<Product[]> {
    return this.request<Product[]>(`/api/v1/businesses/${businessId}/products`);
  }

  // Order methods
  async getUserOrders(): Promise<Order[]> {
    return this.request<Order[]>('/api/v1/orders');
  }

  async createOrder(order: OrderCreate): Promise<Order> {
    return this.request<Order>('/api/v1/orders', {
      method: 'POST',
      body: JSON.stringify(order),
    });
  }

  async getOrder(id: string): Promise<Order> {
    return this.request<Order>(`/api/v1/orders/${id}`);
  }

  async updateOrderStatus(id: string, update: OrderUpdate): Promise<Order> {
    return this.request<Order>(`/api/v1/orders/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify(update),
    });
  }

  async getBusinessOrders(businessId: string): Promise<Order[]> {
    return this.request<Order[]>(`/api/v1/businesses/${businessId}/orders`);
  }

  // Analytics methods
  async getBusinessAnalytics(businessId: string): Promise<BusinessAnalytics> {
    return this.request<BusinessAnalytics>(`/api/v1/businesses/${businessId}/analytics`);
  }

  async getDailySales(businessId: string, days: number = 30): Promise<DailySales[]> {
    return this.request<DailySales[]>(`/api/v1/businesses/${businessId}/analytics/daily?days=${days}`);
  }

  async getDateRangeStats(businessId: string, startDate: string, endDate: string): Promise<DateRangeStats> {
    return this.request<DateRangeStats>(`/api/v1/businesses/${businessId}/analytics/date-range?start_date=${startDate}&end_date=${endDate}`);
  }
}

export const apiService = new ApiService();