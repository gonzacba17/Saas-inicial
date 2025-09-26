import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiService } from '../services/api';

// Mock fetch
global.fetch = vi.fn();

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: vi.fn(() => 'fake-token'),
        setItem: vi.fn(),
        removeItem: vi.fn(),
      },
      writable: true,
    });
  });

  describe('Authentication', () => {
    it('login makes correct API call', async () => {
      const mockResponse = {
        access_token: 'test-token',
        token_type: 'bearer'
      };

      const mockFetch = vi.mocked(fetch);
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const credentials = {
        username: 'testuser',
        password: 'password123'
      };

      const result = await apiService.login(credentials);

      expect(fetch).toHaveBeenCalledWith('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'username=testuser&password=password123',
      });

      expect(result).toEqual(mockResponse);
    });

    it('login handles errors correctly', async () => {
      const mockFetch = vi.mocked(fetch);
      mockFetch.mockResolvedValue({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Invalid credentials' }),
      } as Response);

      const credentials = {
        username: 'testuser',
        password: 'wrongpassword'
      };

      await expect(apiService.login(credentials)).rejects.toThrow();
    });

    it('getCurrentUser makes correct API call', async () => {
      const mockUser = {
        id: '1',
        username: 'testuser',
        email: 'test@example.com',
        role: 'user'
      };

      const mockFetch = vi.mocked(fetch);
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockUser,
      } as Response);

      const result = await apiService.getCurrentUser();

      expect(fetch).toHaveBeenCalledWith('/api/v1/users/me', {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer fake-token',
          'Content-Type': 'application/json',
        },
      });

      expect(result).toEqual(mockUser);
    });
  });

  describe('Businesses', () => {
    it('getBusinesses makes correct API call', async () => {
      const mockBusinesses = [
        {
          id: '1',
          name: 'Test Business',
          description: 'A test business',
          business_type: 'restaurant'
        }
      ];

      const mockFetch = vi.mocked(fetch);
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockBusinesses,
      } as Response);

      const result = await apiService.getBusinesses();

      expect(fetch).toHaveBeenCalledWith('/api/v1/businesses/', {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer fake-token',
          'Content-Type': 'application/json',
        },
      });

      expect(result).toEqual(mockBusinesses);
    });

    it('getBusinessById makes correct API call', async () => {
      const mockBusiness = {
        id: '1',
        name: 'Test Business',
        description: 'A test business',
        business_type: 'restaurant'
      };

      const mockFetch = vi.mocked(fetch);
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockBusiness,
      } as Response);

      const result = await apiService.getBusinessById('1');

      expect(fetch).toHaveBeenCalledWith('/api/v1/businesses/1', {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer fake-token',
          'Content-Type': 'application/json',
        },
      });

      expect(result).toEqual(mockBusiness);
    });

    it('createBusiness makes correct API call', async () => {
      const businessData = {
        name: 'New Business',
        description: 'A new business',
        business_type: 'restaurant',
        address: '123 Test St'
      };

      const mockResponse = {
        id: '2',
        ...businessData
      };

      const mockFetch = vi.mocked(fetch);
      mockFetch.mockResolvedValue({
        ok: true,
        status: 201,
        json: async () => mockResponse,
      } as Response);

      const result = await apiService.createBusiness(businessData);

      expect(fetch).toHaveBeenCalledWith('/api/v1/businesses/', {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer fake-token',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(businessData),
      });

      expect(result).toEqual(mockResponse);
    });
  });

  describe('Products', () => {
    it('getProductsByBusiness makes correct API call', async () => {
      const mockProducts = [
        {
          id: '1',
          name: 'Test Product',
          price: 15.99,
          category: 'food',
          business_id: '1'
        }
      ];

      const mockFetch = vi.mocked(fetch);
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockProducts,
      } as Response);

      const result = await apiService.getProductsByBusiness('1');

      expect(fetch).toHaveBeenCalledWith('/api/v1/businesses/1/products', {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer fake-token',
          'Content-Type': 'application/json',
        },
      });

      expect(result).toEqual(mockProducts);
    });
  });

  describe('Orders', () => {
    it('createOrder makes correct API call', async () => {
      const orderData = {
        business_id: '1',
        items: [
          {
            product_id: '1',
            quantity: 2,
            unit_price: 15.99
          }
        ],
        notes: 'Test order'
      };

      const mockResponse = {
        id: '1',
        ...orderData,
        total_amount: 31.98,
        status: 'PENDING'
      };

      const mockFetch = vi.mocked(fetch);
      mockFetch.mockResolvedValue({
        ok: true,
        status: 201,
        json: async () => mockResponse,
      } as Response);

      const result = await apiService.createOrder(orderData);

      expect(fetch).toHaveBeenCalledWith('/api/v1/orders/', {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer fake-token',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderData),
      });

      expect(result).toEqual(mockResponse);
    });

    it('getUserOrders makes correct API call', async () => {
      const mockOrders = [
        {
          id: '1',
          business_id: '1',
          total_amount: 31.98,
          status: 'PENDING'
        }
      ];

      const mockFetch = vi.mocked(fetch);
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockOrders,
      } as Response);

      const result = await apiService.getUserOrders();

      expect(fetch).toHaveBeenCalledWith('/api/v1/orders/', {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer fake-token',
          'Content-Type': 'application/json',
        },
      });

      expect(result).toEqual(mockOrders);
    });
  });

  describe('Error Handling', () => {
    it('handles network errors', async () => {
      const mockFetch = vi.mocked(fetch);
      mockFetch.mockRejectedValue(new Error('Network error'));

      await expect(apiService.getBusinesses()).rejects.toThrow('Network error');
    });

    it('handles HTTP errors', async () => {
      const mockFetch = vi.mocked(fetch);
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Internal server error' }),
      } as Response);

      await expect(apiService.getBusinesses()).rejects.toThrow();
    });

    it('handles authentication errors', async () => {
      const mockFetch = vi.mocked(fetch);
      mockFetch.mockResolvedValue({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Unauthorized' }),
      } as Response);

      await expect(apiService.getCurrentUser()).rejects.toThrow();
    });
  });

  describe('Request Headers', () => {
    it('includes authorization header when token exists', async () => {
      const mockFetch = vi.mocked(fetch);
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => [],
      } as Response);

      await apiService.getBusinesses();

      expect(fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer fake-token'
          })
        })
      );
    });

    it('handles missing token gracefully', async () => {
      // Mock localStorage to return null
      vi.mocked(localStorage.getItem).mockReturnValue(null);

      const mockFetch = vi.mocked(fetch);
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => [],
      } as Response);

      await apiService.getBusinesses();

      expect(fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer null'
          })
        })
      );
    });
  });
});