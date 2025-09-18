import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import { Dashboard } from '../pages/Dashboard';

// Mock the auth store
vi.mock('../store/authStore', () => ({
  useAuthStore: () => ({
    user: { username: 'testuser', email: 'test@example.com' },
    logout: vi.fn(),
  }),
}));

// Mock fetch
global.fetch = vi.fn();

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
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
  it('renders loading state initially', () => {
    renderDashboard();
    
    expect(screen.getByText('Loading dashboard...')).toBeInTheDocument();
  });

  it('renders dashboard header', () => {
    // Mock successful fetch
    (global.fetch as any).mockResolvedValueOnce({
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
    });

    renderDashboard();
    
    expect(screen.getByText('📊 Sales Dashboard')).toBeInTheDocument();
  });
});