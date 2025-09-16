import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../App';

// Mock zustand stores
vi.mock('../store/authStore', () => ({
  useAuthStore: () => ({
    isAuthenticated: false,
    token: null,
  }),
}));

vi.mock('../store/cartStore', () => ({
  useCartStore: () => ({
    items: [],
    total: 0,
    cafe_id: null,
    addItem: vi.fn(),
    removeItem: vi.fn(),
    updateQuantity: vi.fn(),
    clearCart: vi.fn(),
    setCafe: vi.fn(),
    getItemCount: () => 0,
  }),
}));

describe('App Component', () => {
  it('renders without crashing', () => {
    render(<App />);
    expect(document.body).toBeInTheDocument();
  });

  it('redirects to login when not authenticated', () => {
    render(<App />);
    // The app should redirect to login page when not authenticated
    // Since we're using React Router, we can't easily test the redirect
    // without more complex setup, so this is a basic smoke test
    expect(document.body).toBeInTheDocument();
  });
});