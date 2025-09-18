import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useCartStore } from '../store/cartStore';
import { useAuthStore } from '../store/authStore';
import { apiService } from '../services/api';
import { Business, Product } from '../types/business';


export const BusinessDetail: React.FC = () => {
  const { businessId } = useParams<{ businessId: string }>();
  const navigate = useNavigate();
  const [business, setBusiness] = useState<Business | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');

  const { addItem, items, getItemCount } = useCartStore();
  const { user, logout } = useAuthStore();

  // Mock data for now - will connect to API later
  useEffect(() => {
    const mockBusiness: Business = {
      id: businessId || '1',
      name: 'Central Coffee',
      description: 'Premium coffee experience in the heart of the city',
      address: '123 Main St, Downtown',
      business_type: 'restaurant',
    };

    const mockProducts: Product[] = [
      {
        id: '1',
        name: 'Espresso',
        description: 'Rich and bold espresso shot',
        price: 3.50,
        category: 'coffee',
        business_id: businessId || '1',
      },
      {
        id: '2',
        name: 'Cappuccino',
        description: 'Espresso with steamed milk and foam',
        price: 4.50,
        category: 'coffee',
        business_id: businessId || '1',
      },
      {
        id: '3',
        name: 'Croissant',
        description: 'Buttery, flaky pastry',
        price: 3.00,
        category: 'pastry',
        business_id: businessId || '1',
      },
      {
        id: '4',
        name: 'Avocado Toast',
        description: 'Fresh avocado on artisan bread',
        price: 8.50,
        category: 'food',
        business_id: businessId || '1',
      },
      {
        id: '5',
        name: 'Latte',
        description: 'Smooth espresso with steamed milk',
        price: 4.75,
        category: 'coffee',
        business_id: businessId || '1',
      },
    ];

    // Simulate API call
    setTimeout(() => {
      setBusiness(mockBusiness);
      setProducts(mockProducts);
      setLoading(false);
    }, 1000);
  }, [businessId]);

  const categories = ['all', ...Array.from(new Set(products.map(p => p.category)))];
  
  const filteredProducts = selectedCategory === 'all' 
    ? products 
    : products.filter(p => p.category === selectedCategory);

  const handleAddToCart = (product: Product) => {
    addItem(product);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const goToCheckout = () => {
    navigate('/checkout');
  };

  const getBusinessTypeIcon = (type: string) => {
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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading business details...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/businesses')}
                className="text-gray-600 hover:text-gray-900"
              >
                ← Back to Businesses
              </button>
              <h1 className="text-xl font-semibold text-gray-900">
                {getBusinessTypeIcon(business?.business_type || 'general')} {business?.name}
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={goToCheckout}
                className="relative bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Cart ({getItemCount()})
                {getItemCount() > 0 && (
                  <span className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">
                    {getItemCount()}
                  </span>
                )}
              </button>
              <span className="text-gray-700">{user?.username}</span>
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

      {/* Business Info */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex items-center space-x-3">
            <span className="text-4xl">{getBusinessTypeIcon(business?.business_type || 'general')}</span>
            <div>
              <h2 className="text-3xl font-bold text-gray-900">{business?.name}</h2>
              <p className="mt-2 text-gray-600">{business?.description}</p>
              <p className="mt-1 text-sm text-gray-500">📍 {business?.address}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Category Filter */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8 py-4">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`capitalize font-medium text-sm ${
                  selectedCategory === category
                    ? 'text-indigo-600 border-b-2 border-indigo-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Products */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {filteredProducts.map((product) => (
              <div
                key={product.id}
                className="bg-white overflow-hidden shadow rounded-lg"
              >
                <div className="p-6">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="text-lg font-medium text-gray-900">{product.name}</h3>
                      <p className="mt-1 text-sm text-gray-600">{product.description}</p>
                      <p className="mt-2 text-sm text-gray-500 capitalize">
                        Category: {product.category}
                      </p>
                    </div>
                  </div>
                  <div className="mt-4 flex justify-between items-center">
                    <span className="text-2xl font-bold text-gray-900">
                      ${product.price.toFixed(2)}
                    </span>
                    <button
                      onClick={() => handleAddToCart(product)}
                      className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                    >
                      Add to Cart
                    </button>
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