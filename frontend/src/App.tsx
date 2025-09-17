import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Businesses } from './pages/Businesses';
import { BusinessDetail } from './pages/BusinessDetail';
import { Checkout } from './pages/Checkout';

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
    <Router>
      <Routes>
        {/* Public routes */}
        <Route 
          path="/login" 
          element={!isAuthenticated ? <Login /> : <Navigate to="/businesses" />} 
        />
        <Route 
          path="/register" 
          element={!isAuthenticated ? <Register /> : <Navigate to="/businesses" />} 
        />
        
        {/* Protected routes */}
        <Route 
          path="/businesses" 
          element={isAuthenticated ? <Businesses /> : <Navigate to="/login" />} 
        />
        <Route 
          path="/businesses/:businessId" 
          element={isAuthenticated ? <BusinessDetail /> : <Navigate to="/login" />} 
        />
        <Route 
          path="/checkout" 
          element={isAuthenticated ? <Checkout /> : <Navigate to="/login" />} 
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
  );
}

export default App;
