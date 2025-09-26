import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import { Dashboard } from '../pages/Dashboard';

// Mock the auth store
const mockUser = {
  id: '1',
  username: 'testuser',
  email: 'test@example.com',
  role: 'user'
};

vi.mock('../store/authStore', () => ({
  useAuthStore: () => ({
    user: mockUser,
    logout: vi.fn(),
  }),
}));

// Mock fetch
global.fetch = vi.fn();

// Mock react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const renderDashboard = () => {
  return render(
    <BrowserRouter>
      <Dashboard />
    </BrowserRouter>
  );
};

describe('Dashboard Component', () => {
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

  it('renders loading state initially', () => {
    const mockFetch = vi.mocked(fetch);
    mockFetch.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    renderDashboard();
    
    expect(screen.getByText('Loading dashboard...')).toBeInTheDocument();
  });

  it('renders dashboard header after loading', async () => {
    const mockFetch = vi.mocked(fetch);
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        period_days: 30,
        total_sales: 1000,
        total_orders: 10,
        average_order_value: 100,
        daily_sales: [],
        top_products: [],
        business_name: null
      }),
    } as Response);

    renderDashboard();
    
    await waitFor(() => {
      expect(screen.getByText('📊 Sales Dashboard')).toBeInTheDocument();
    });
  });

  it('displays user information', async () => {
    const mockFetch = vi.mocked(fetch);
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        period_days: 30,
        total_sales: 1000,
        total_orders: 10,
        average_order_value: 100,
        daily_sales: [],
        top_products: [],
        business_name: null
      }),
    } as Response);

    renderDashboard();
    
    await waitFor(() => {
      expect(screen.getByText(`Welcome, ${mockUser.username}`)).toBeInTheDocument();
    });
  });

  it('handles API error gracefully', async () => {
    const mockFetch = vi.mocked(fetch);
    mockFetch.mockResolvedValue({
      ok: false,
      status: 500,
    } as Response);

    renderDashboard();
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load analytics data')).toBeInTheDocument();
    });
  });

  it('displays KPI cards', async () => {
    const mockFetch = vi.mocked(fetch);
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        period_days: 30,
        total_sales: 1500.50,
        total_orders: 75,
        average_order_value: 20.01,
        daily_sales: [],
        top_products: [],
        business_name: null
      }),
    } as Response);

    renderDashboard();
    
    await waitFor(() => {
      expect(screen.getByText('Total Sales')).toBeInTheDocument();
      expect(screen.getByText('Total Orders')).toBeInTheDocument();
      expect(screen.getByText('Avg Order Value')).toBeInTheDocument();
      expect(screen.getByText('75')).toBeInTheDocument();
    });
  });
});