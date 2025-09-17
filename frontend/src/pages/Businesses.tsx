import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { apiService } from '../services/api';
import { Business } from '../types/business';

export const Businesses: React.FC = () => {
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  // Fetch businesses from API
  useEffect(() => {
    const fetchBusinesses = async () => {
      try {
        const data = await apiService.getBusinesses();
        setBusinesses(data);
      } catch (err) {
        setError('Failed to load businesses');
        console.error('Error fetching businesses:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchBusinesses();
  }, []);

  const handleBusinessClick = (businessId: string) => {
    navigate(`/businesses/${businessId}`);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getBusinessIcon = (type: string) => {
    switch (type) {
      case 'restaurant':
        return '🍽️';
      case 'store':
        return '🏪';
      case 'service':
        return '⚙️';
      default:
        return '🏢';
    }
  };

  const getBusinessTypeLabel = (type: string) => {
    switch (type) {
      case 'restaurant':
        return 'Restaurant';
      case 'store':
        return 'Store';
      case 'service':
        return 'Service';
      default:
        return 'Business';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading businesses...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-xl text-red-600 mb-4">{error}</div>
          <button 
            onClick={() => window.location.reload()} 
            className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">🚀 ModularBiz SaaS</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Welcome, {user?.username}</span>
              <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Available Businesses</h2>
            <p className="mt-1 text-sm text-gray-600">
              Choose a business to view their products and services
            </p>
          </div>

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {businesses.map((business) => (
              <div
                key={business.id}
                onClick={() => handleBusinessClick(business.id)}
                className="bg-white overflow-hidden shadow rounded-lg cursor-pointer hover:shadow-lg transition-shadow duration-200"
              >
                <div className="p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="h-12 w-12 bg-indigo-500 rounded-md flex items-center justify-center">
                        <span className="text-white font-bold text-lg">
                          {getBusinessIcon(business.business_type)}
                        </span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <h3 className="text-lg font-medium text-gray-900">{business.name}</h3>
                      <p className="text-sm text-gray-500">{business.address}</p>
                    </div>
                  </div>
                  <div className="mt-4">
                    <p className="text-sm text-gray-600">{business.description}</p>
                  </div>
                  <div className="mt-4 flex justify-between items-center">
                    <div className="text-sm text-gray-500">
                      <p>📞 {business.phone}</p>
                      <p>✉️ {business.email}</p>
                    </div>
                    <div className="text-right">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mb-1">
                        {getBusinessTypeLabel(business.business_type)}
                      </span>
                      <br />
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Active
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};