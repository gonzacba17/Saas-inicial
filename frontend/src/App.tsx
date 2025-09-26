import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Businesses } from './pages/Businesses';
import { BusinessDetail } from './pages/BusinessDetail';
import { Checkout } from './pages/Checkout';
import { Orders } from './pages/Orders';
import { BusinessDashboard } from './pages/BusinessDashboard';
import { Dashboard } from './pages/Dashboard';

function App() {
  const { isAuthenticated, token } = useAuthStore();

  // Initialize auth state from localStorage on app start
  useEffect(() => {
    const storedToken = localStorage.getItem('access_token');
    if (storedToken && !token) {
      // Token exists but store is not initialized
      // This could be improved with a proper token validation
    }
  }, [token]);

  return (
    <ErrorBoundary>
      <Router>
        <Routes>
          {/* Public routes */}
          <Route 
            path="/login" 
            element={!isAuthenticated ? (
              <ErrorBoundary>
                <Login />
              </ErrorBoundary>
            ) : <Navigate to="/businesses" />} 
          />
          <Route 
            path="/register" 
            element={!isAuthenticated ? (
              <ErrorBoundary>
                <Register />
              </ErrorBoundary>
            ) : <Navigate to="/businesses" />} 
          />
          
          {/* Protected routes */}
          <Route 
            path="/businesses" 
            element={isAuthenticated ? (
              <ErrorBoundary>
                <Businesses />
              </ErrorBoundary>
            ) : <Navigate to="/login" />} 
          />
          <Route 
            path="/businesses/:businessId" 
            element={isAuthenticated ? (
              <ErrorBoundary>
                <BusinessDetail />
              </ErrorBoundary>
            ) : <Navigate to="/login" />} 
          />
          <Route 
            path="/checkout" 
            element={isAuthenticated ? (
              <ErrorBoundary>
                <Checkout />
              </ErrorBoundary>
            ) : <Navigate to="/login" />} 
          />
          <Route 
            path="/orders" 
            element={isAuthenticated ? (
              <ErrorBoundary>
                <Orders />
              </ErrorBoundary>
            ) : <Navigate to="/login" />} 
          />
          <Route 
            path="/businesses/:businessId/dashboard" 
            element={isAuthenticated ? (
              <ErrorBoundary>
                <BusinessDashboard />
              </ErrorBoundary>
            ) : <Navigate to="/login" />} 
          />
          <Route 
            path="/dashboard" 
            element={isAuthenticated ? (
              <ErrorBoundary>
                <Dashboard />
              </ErrorBoundary>
            ) : <Navigate to="/login" />} 
          />
          
          {/* Default redirect */}
          <Route 
            path="/" 
            element={<Navigate to={isAuthenticated ? "/businesses" : "/login"} />} 
          />
          
          {/* Catch all route */}
          <Route 
            path="*" 
            element={<Navigate to={isAuthenticated ? "/businesses" : "/login"} />} 
          />
        </Routes>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
