import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import { Register } from '../pages/Register';

// Mock the auth store
vi.mock('../store/authStore', () => ({
  useAuthStore: () => ({
    login: vi.fn(),
  }),
}));

// Mock the API service
vi.mock('../services/api', () => ({
  apiService: {
    register: vi.fn(),
    getCurrentUser: vi.fn(),
  },
}));

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  };
});

const renderRegister = () => {
  return render(
    <BrowserRouter>
      <Register />
    </BrowserRouter>
  );
};

describe('Register Component', () => {
  it('renders registration form', () => {
    renderRegister();
    
    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Username')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
  });

  it('allows user to type in all fields', () => {
    renderRegister();
    
    const emailInput = screen.getByPlaceholderText('Email') as HTMLInputElement;
    const usernameInput = screen.getByPlaceholderText('Username') as HTMLInputElement;
    const passwordInput = screen.getByPlaceholderText('Password') as HTMLInputElement;

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'testpass123' } });

    expect(emailInput.value).toBe('test@example.com');
    expect(usernameInput.value).toBe('testuser');
    expect(passwordInput.value).toBe('testpass123');
  });

  it('has sign in navigation link', () => {
    renderRegister();
    
    expect(screen.getByText('Already have an account? Sign in')).toBeInTheDocument();
  });
});