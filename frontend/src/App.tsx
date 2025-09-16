import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Cafes } from './pages/Cafes';
import { CafeDetail } from './pages/CafeDetail';
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
          element={!isAuthenticated ? <Login /> : <Navigate to="/cafes" />} 
        />
        <Route 
          path="/register" 
          element={!isAuthenticated ? <Register /> : <Navigate to="/cafes" />} 
        />
        
        {/* Protected routes */}
        <Route 
          path="/cafes" 
          element={isAuthenticated ? <Cafes /> : <Navigate to="/login" />} 
        />
        <Route 
          path="/cafes/:cafeId" 
          element={isAuthenticated ? <CafeDetail /> : <Navigate to="/login" />} 
        />
        <Route 
          path="/checkout" 
          element={isAuthenticated ? <Checkout /> : <Navigate to="/login" />} 
        />
        
        {/* Default redirect */}
        <Route 
          path="/" 
          element={<Navigate to={isAuthenticated ? "/cafes" : "/login"} />} 
        />
        
        {/* Catch all route */}
        <Route 
          path="*" 
          element={<Navigate to={isAuthenticated ? "/cafes" : "/login"} />} 
        />
      </Routes>
    </Router>
  );
}

export default App;
