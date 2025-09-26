import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi } from 'vitest';
import { Login } from '../pages/Login';
import { apiService } from '../services/api';

// Mock the API service
vi.mock('../services/api', () => ({
  apiService: {
    login: vi.fn(),
    getCurrentUser: vi.fn(),
  },
}));

// Mock the auth store
vi.mock('../store/authStore', () => ({
  useAuthStore: () => ({
    login: vi.fn(),
  }),
}));

// Mock router navigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const LoginWithRouter = () => (
  <BrowserRouter>
    <Login />
  </BrowserRouter>
);

describe('Login Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders login form', () => {
    render(<LoginWithRouter />);
    
    expect(screen.getByPlaceholderText('Username')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  test('displays app title', () => {
    render(<LoginWithRouter />);
    
    expect(screen.getByText('Sign in to Cafeteria IA')).toBeInTheDocument();
    expect(screen.getByText('Intelligent cafe management system')).toBeInTheDocument();
  });

  test('allows user to input credentials', async () => {
    render(<LoginWithRouter />);
    
    const usernameInput = screen.getByPlaceholderText('Username');
    const passwordInput = screen.getByPlaceholderText('Password');
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    
    expect(usernameInput).toHaveValue('testuser');
    expect(passwordInput).toHaveValue('password123');
  });

  test('successful login redirects to businesses page', async () => {
    const mockApiLogin = vi.mocked(apiService.login);
    const mockGetCurrentUser = vi.mocked(apiService.getCurrentUser);
    
    mockApiLogin.mockResolvedValue({ access_token: 'fake-token' });
    mockGetCurrentUser.mockResolvedValue({
      id: '1',
      username: 'testuser',
      email: 'test@example.com',
      role: 'user'
    });
    
    render(<LoginWithRouter />);
    
    fireEvent.change(screen.getByPlaceholderText('Username'), {
      target: { value: 'testuser' }
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: 'password123' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
    
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/businesses');
    });
  });

  test('handles login error', async () => {
    const mockApiLogin = vi.mocked(apiService.login);
    mockApiLogin.mockRejectedValue(new Error('Invalid credentials'));
    
    render(<LoginWithRouter />);
    
    fireEvent.change(screen.getByPlaceholderText('Username'), {
      target: { value: 'testuser' }
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: 'wrongpassword' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
    
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  test('disables submit button during loading', async () => {
    const mockApiLogin = vi.mocked(apiService.login);
    mockApiLogin.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    render(<LoginWithRouter />);
    
    fireEvent.change(screen.getByPlaceholderText('Username'), {
      target: { value: 'testuser' }
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: 'password123' }
    });
    
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Signing in...')).toBeInTheDocument();
      expect(submitButton).toBeDisabled();
    });
  });

  test('navigates to register page when register link is clicked', () => {
    render(<LoginWithRouter />);
    
    const registerLink = screen.getByText("Don't have an account? Sign up");
    fireEvent.click(registerLink);
    
    expect(mockNavigate).toHaveBeenCalledWith('/register');
  });

  test('form validation requires username and password', () => {
    render(<LoginWithRouter />);
    
    const usernameInput = screen.getByPlaceholderText('Username');
    const passwordInput = screen.getByPlaceholderText('Password');
    
    expect(usernameInput).toBeRequired();
    expect(passwordInput).toBeRequired();
  });
});