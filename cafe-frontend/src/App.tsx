import React, { useState, useEffect } from 'react';
import { LoginForm } from './components/LoginForm';
import { RegisterForm } from './components/RegisterForm';
import { Dashboard } from './components/Dashboard';

type ViewType = 'login' | 'register' | 'dashboard';

function App() {
  const [currentView, setCurrentView] = useState<ViewType>('login');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsAuthenticated(true);
      setCurrentView('dashboard');
    }
  }, []);

  const handleLogin = (token: string) => {
    setIsAuthenticated(true);
    setCurrentView('dashboard');
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentView('login');
    localStorage.removeItem('access_token');
  };

  const handleRegister = () => {
    setCurrentView('login');
  };

  const switchToLogin = () => setCurrentView('login');
  const switchToRegister = () => setCurrentView('register');

  if (currentView === 'dashboard' && isAuthenticated) {
    return <Dashboard onLogout={handleLogout} />;
  }

  if (currentView === 'register') {
    return (
      <RegisterForm
        onRegister={handleRegister}
        onSwitchToLogin={switchToLogin}
      />
    );
  }

  return (
    <LoginForm
      onLogin={handleLogin}
      onSwitchToRegister={switchToRegister}
    />
  );
}

export default App;
