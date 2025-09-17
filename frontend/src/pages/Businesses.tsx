import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

interface Business {
  id: string;
  name: string;
  description: string;
  address: string;
  phone: string;
  email: string;
  business_type: string;
  is_active: boolean;
}

export const Businesses: React.FC = () => {
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  // Mock data for now - will connect to API later
  useEffect(() => {
    const mockBusinesses: Business[] = [
      {
        id: '1',
        name: 'Central Coffee',
        description: 'Premium coffee experience in the heart of the city',
        address: '123 Main St, Downtown',
        phone: '+1 (555) 123-4567',
        email: 'info@centralcoffee.com',
        business_type: 'restaurant',
        is_active: true,
      },
      {
        id: '2',
        name: 'Tech Store Pro',
        description: 'Latest technology and gadgets for professionals',
        address: '456 Tech Ave, Innovation District',
        phone: '+1 (555) 234-5678',
        email: 'hello@techstorepro.com',
        business_type: 'store',
        is_active: true,
      },
      {
        id: '3',
        name: 'Garden Services',
        description: 'Professional landscaping and garden maintenance',
        address: '789 Garden Blvd, Green Valley',
        phone: '+1 (555) 345-6789',
        email: 'contact@gardenservices.com',
        business_type: 'service',
        is_active: true,
      },
    ];

    // Simulate API call
    setTimeout(() => {
      setBusinesses(mockBusinesses);
      setLoading(false);
    }, 1000);
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