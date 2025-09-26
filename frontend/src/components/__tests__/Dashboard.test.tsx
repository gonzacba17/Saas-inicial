import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import Dashboard from '../Dashboard';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../contexts/AuthContext';

// Mock fetch globally
global.fetch = vi.fn();

const DashboardWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>
    <AuthProvider>
      {children}
    </AuthProvider>
  </BrowserRouter>
);

describe('Dashboard Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock successful auth check
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({ 
        id: 'user-123', 
        username: 'testuser', 
        email: 'test@example.com',
        role: 'user'
      }),
    });
  });

  it('renders dashboard title and navigation', async () => {
    render(
      <DashboardWrapper>
        <Dashboard />
      </DashboardWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });

    expect(screen.getByText(/Bienvenido/i)).toBeInTheDocument();
  });

  it('displays user information when loaded', async () => {
    render(
      <DashboardWrapper>
        <Dashboard />
      </DashboardWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/testuser/i)).toBeInTheDocument();
    });
  });

  it('shows loading state initially', () => {
    render(
      <DashboardWrapper>
        <Dashboard />
      </DashboardWrapper>
    );

    expect(screen.getByText(/cargando/i)).toBeInTheDocument();
  });

  it('handles user data fetch error gracefully', async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error('API Error'));

    render(
      <DashboardWrapper>
        <Dashboard />
      </DashboardWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/error al cargar/i)).toBeInTheDocument();
    });
  });

  it('displays navigation links correctly', async () => {
    render(
      <DashboardWrapper>
        <Dashboard />
      </DashboardWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });

    // Check for navigation elements
    expect(screen.getByText(/Mis Negocios/i)).toBeInTheDocument();
    expect(screen.getByText(/Pedidos/i)).toBeInTheDocument();
    expect(screen.getByText(/Perfil/i)).toBeInTheDocument();
  });

  it('shows appropriate content for admin users', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ 
        id: 'admin-123', 
        username: 'admin', 
        email: 'admin@example.com',
        role: 'admin'
      }),
    });

    render(
      <DashboardWrapper>
        <Dashboard />
      </DashboardWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Panel de Administración/i)).toBeInTheDocument();
    });
  });

  it('shows recent activity section', async () => {
    render(
      <DashboardWrapper>
        <Dashboard />
      </DashboardWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Actividad Reciente/i)).toBeInTheDocument();
    });
  });

  it('displays statistics cards', async () => {
    render(
      <DashboardWrapper>
        <Dashboard />
      </DashboardWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Total Pedidos/i)).toBeInTheDocument();
      expect(screen.getByText(/Ventas del Mes/i)).toBeInTheDocument();
      expect(screen.getByText(/Negocios Activos/i)).toBeInTheDocument();
    });
  });

  it('handles unauthorized access appropriately', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ detail: 'Unauthorized' }),
    });

    render(
      <DashboardWrapper>
        <Dashboard />
      </DashboardWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/No autorizado/i)).toBeInTheDocument();
    });
  });
});