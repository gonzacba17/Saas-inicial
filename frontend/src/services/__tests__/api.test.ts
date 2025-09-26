import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as api from '../api';

// Mock fetch globally
global.fetch = vi.fn();

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('Authentication', () => {
    it('should login successfully', async () => {
      const mockResponse = {
        access_token: 'test-token',
        token_type: 'bearer',
        user_id: 'user-123',
        role: 'user'
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await api.login('testuser', 'password123');

      expect(global.fetch).toHaveBeenCalledWith('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'username=testuser&password=password123',
      });

      expect(result).toEqual(mockResponse);
    });

    it('should handle login failure', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Invalid credentials' }),
      });

      await expect(api.login('wronguser', 'wrongpass')).rejects.toThrow('Invalid credentials');
    });

    it('should register user successfully', async () => {
      const mockUser = {
        id: 'user-123',
        username: 'newuser',
        email: 'new@example.com',
        role: 'user'
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockUser,
      });

      const userData = {
        username: 'newuser',
        email: 'new@example.com',
        password: 'password123'
      };

      const result = await api.register(userData);

      expect(global.fetch).toHaveBeenCalledWith('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
      });

      expect(result).toEqual(mockUser);
    });

    it('should get current user successfully', async () => {
      const mockUser = {
        id: 'user-123',
        username: 'testuser',
        email: 'test@example.com',
        role: 'user'
      };

      localStorage.setItem('token', 'test-token');

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockUser,
      });

      const result = await api.getCurrentUser();

      expect(global.fetch).toHaveBeenCalledWith('/api/v1/auth/me', {
        headers: { 'Authorization': 'Bearer test-token' },
      });

      expect(result).toEqual(mockUser);
    });
  });

  describe('Business Operations', () => {
    beforeEach(() => {
      localStorage.setItem('token', 'test-token');
    });

    it('should fetch businesses successfully', async () => {
      const mockBusinesses = [
        { id: 'biz-1', name: 'Business 1', type: 'restaurant' },
        { id: 'biz-2', name: 'Business 2', type: 'cafe' }
      ];

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockBusinesses,
      });

      const result = await api.getBusinesses();

      expect(global.fetch).toHaveBeenCalledWith('/api/v1/businesses', {
        headers: { 'Authorization': 'Bearer test-token' },
      });

      expect(result).toEqual(mockBusinesses);
    });

    it('should create business successfully', async () => {
      const newBusiness = {
        name: 'New Business',
        description: 'A test business',
        business_type: 'restaurant'
      };

      const mockResponse = {
        id: 'biz-123',
        ...newBusiness
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await api.createBusiness(newBusiness);

      expect(global.fetch).toHaveBeenCalledWith('/api/v1/businesses', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token',
        },
        body: JSON.stringify(newBusiness),
      });

      expect(result).toEqual(mockResponse);
    });

    it('should get business by ID successfully', async () => {
      const mockBusiness = {
        id: 'biz-123',
        name: 'Test Business',
        description: 'A test business'
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockBusiness,
      });

      const result = await api.getBusiness('biz-123');

      expect(global.fetch).toHaveBeenCalledWith('/api/v1/businesses/biz-123', {
        headers: { 'Authorization': 'Bearer test-token' },
      });

      expect(result).toEqual(mockBusiness);
    });
  });

  describe('Order Operations', () => {
    beforeEach(() => {
      localStorage.setItem('token', 'test-token');
    });

    it('should create order successfully', async () => {
      const orderData = {
        business_id: 'biz-123',
        items: [
          {
            product_id: 'prod-1',
            quantity: 2,
            unit_price: 10.50
          }
        ]
      };

      const mockOrder = {
        id: 'order-123',
        ...orderData,
        total_amount: 21.00,
        status: 'PENDING'
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockOrder,
      });

      const result = await api.createOrder(orderData);

      expect(global.fetch).toHaveBeenCalledWith('/api/v1/orders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token',
        },
        body: JSON.stringify(orderData),
      });

      expect(result).toEqual(mockOrder);
    });

    it('should get user orders successfully', async () => {
      const mockOrders = [
        { id: 'order-1', total_amount: 25.50, status: 'PENDING' },
        { id: 'order-2', total_amount: 15.75, status: 'DELIVERED' }
      ];

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockOrders,
      });

      const result = await api.getUserOrders();

      expect(global.fetch).toHaveBeenCalledWith('/api/v1/orders/user', {
        headers: { 'Authorization': 'Bearer test-token' },
      });

      expect(result).toEqual(mockOrders);
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

      await expect(api.login('user', 'pass')).rejects.toThrow('Network error');
    });

    it('should handle 404 errors', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Not found' }),
      });

      localStorage.setItem('token', 'test-token');

      await expect(api.getBusiness('nonexistent')).rejects.toThrow('Not found');
    });

    it('should handle unauthorized errors', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Unauthorized' }),
      });

      await expect(api.getCurrentUser()).rejects.toThrow('Unauthorized');
    });

    it('should handle validation errors', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 422,
        json: async () => ({ detail: 'Validation error' }),
      });

      localStorage.setItem('token', 'test-token');

      const invalidBusiness = { name: '' }; // Invalid data

      await expect(api.createBusiness(invalidBusiness)).rejects.toThrow('Validation error');
    });
  });

  describe('Token Management', () => {
    it('should include auth token in requests when available', async () => {
      localStorage.setItem('token', 'test-token');

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      await api.getBusinesses();

      expect(global.fetch).toHaveBeenCalledWith('/api/v1/businesses', {
        headers: { 'Authorization': 'Bearer test-token' },
      });
    });

    it('should make requests without auth token when not available', async () => {
      localStorage.removeItem('token');

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ access_token: 'new-token' }),
      });

      await api.login('user', 'pass');

      expect(global.fetch).toHaveBeenCalledWith('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'username=user&password=pass',
      });
    });
  });
});