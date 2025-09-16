import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

interface Cafe {
  id: string;
  name: string;
  description: string;
  address: string;
  phone: string;
  email: string;
  is_active: boolean;
}

export const Cafes: React.FC = () => {
  const [cafes, setCafes] = useState<Cafe[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  // Mock data for now
  useEffect(() => {
    const mockCafes: Cafe[] = [
      {
        id: '1',
        name: 'Central Coffee',
        description: 'Premium coffee experience in the heart of the city',
        address: '123 Main St, Downtown',
        phone: '+1 (555) 123-4567',
        email: 'info@centralcoffee.com',
        is_active: true,
      },
      {
        id: '2',
        name: 'Artisan Roasters',
        description: 'Hand-crafted coffee from locally sourced beans',
        address: '456 Oak Ave, Arts District',
        phone: '+1 (555) 234-5678',
        email: 'hello@artisanroasters.com',
        is_active: true,
      },
      {
        id: '3',
        name: 'Garden Café',
        description: 'Peaceful garden setting with organic options',
        address: '789 Garden Blvd, Green Valley',
        phone: '+1 (555) 345-6789',
        email: 'contact@gardencafe.com',
        is_active: true,
      },
    ];

    // Simulate API call
    setTimeout(() => {
      setCafes(mockCafes);
      setLoading(false);
    }, 1000);
  }, []);

  const handleCafeClick = (cafeId: string) => {
    navigate(`/cafes/${cafeId}`);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading cafes...</div>
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
              <h1 className="text-xl font-semibold text-gray-900">☕ Cafeteria IA</h1>
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
            <h2 className="text-2xl font-bold text-gray-900">Available Cafes</h2>
            <p className="mt-1 text-sm text-gray-600">
              Choose a cafe to view their menu and place orders
            </p>
          </div>

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {cafes.map((cafe) => (
              <div
                key={cafe.id}
                onClick={() => handleCafeClick(cafe.id)}
                className="bg-white overflow-hidden shadow rounded-lg cursor-pointer hover:shadow-lg transition-shadow duration-200"
              >
                <div className="p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="h-12 w-12 bg-indigo-500 rounded-md flex items-center justify-center">
                        <span className="text-white font-bold text-lg">☕</span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <h3 className="text-lg font-medium text-gray-900">{cafe.name}</h3>
                      <p className="text-sm text-gray-500">{cafe.address}</p>
                    </div>
                  </div>
                  <div className="mt-4">
                    <p className="text-sm text-gray-600">{cafe.description}</p>
                  </div>
                  <div className="mt-4 flex justify-between items-center">
                    <div className="text-sm text-gray-500">
                      <p>📞 {cafe.phone}</p>
                      <p>✉️ {cafe.email}</p>
                    </div>
                    <div className="text-right">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Open
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