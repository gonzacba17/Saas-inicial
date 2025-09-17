import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCartStore } from '../store/cartStore';
import { useAuthStore } from '../store/authStore';
import { apiService } from '../services/api';
import { OrderCreate } from '../types/order';

export const Checkout: React.FC = () => {
  const navigate = useNavigate();
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [orderPlaced, setOrderPlaced] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { items, total, clearCart, removeItem, updateQuantity } = useCartStore();
  const { user, logout } = useAuthStore();

  const handleQuantityChange = (productId: string, newQuantity: number) => {
    if (newQuantity <= 0) {
      removeItem(productId);
    } else {
      updateQuantity(productId, newQuantity);
    }
  };

  const handlePlaceOrder = async () => {
    if (items.length === 0) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // Get business_id from first item (all items should be from same business)
      const business_id = items[0].product.business_id;
      
      // Create order payload
      const orderData: OrderCreate = {
        business_id,
        notes: notes.trim() || undefined,
        items: items.map(item => ({
          product_id: item.product.id,
          quantity: item.quantity,
          unit_price: item.product.price
        }))
      };

      // Create order via API
      await apiService.createOrder(orderData);
      
      setOrderPlaced(true);
      clearCart();
    } catch (err) {
      console.error('Error placing order:', err);
      setError(err instanceof Error ? err.message : 'Failed to place order');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (orderPlaced) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8 text-center">
          <div className="text-green-500 text-6xl mb-4">✅</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Order Placed!</h2>
          <p className="text-gray-600 mb-6">
            Your order has been successfully placed. You will receive a confirmation soon.
          </p>
          <div className="space-y-3">
            <button
              onClick={() => navigate('/orders')}
              className="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md font-medium"
            >
              View My Orders
            </button>
            <button
              onClick={() => navigate('/businesses')}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md font-medium"
            >
              Continue Shopping
            </button>
          </div>
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
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/businesses')}
                className="text-gray-600 hover:text-gray-900"
              >
                ← Back to Businesses
              </button>
              <h1 className="text-xl font-semibold text-gray-900">Checkout</h1>
            </div>
            <div className="flex items-center space-x-4">
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

      <main className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {items.length === 0 ? (
            <div className="bg-white rounded-lg shadow p-8 text-center">
              <div className="text-gray-400 text-6xl mb-4">🛒</div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Your cart is empty</h2>
              <p className="text-gray-600 mb-6">
                Add some delicious items from our businesses to get started!
              </p>
              <button
                onClick={() => navigate('/businesses')}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-md font-medium"
              >
                Browse Businesses
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Cart Items */}
              <div className="lg:col-span-2">
                <div className="bg-white rounded-lg shadow">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h2 className="text-lg font-medium text-gray-900">Your Order</h2>
                  </div>
                  <div className="px-6 py-4">
                    <div className="space-y-4">
                      {items.map((item) => (
                        <div key={item.product.id} className="flex items-center justify-between py-4 border-b border-gray-200 last:border-b-0">
                          <div className="flex-1">
                            <h3 className="text-sm font-medium text-gray-900">
                              {item.product.name}
                            </h3>
                            <p className="text-sm text-gray-500">
                              {item.product.description}
                            </p>
                            <p className="text-sm font-medium text-gray-900 mt-1">
                              ${item.product.price.toFixed(2)} each
                            </p>
                          </div>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => handleQuantityChange(item.product.id, item.quantity - 1)}
                              className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 hover:bg-gray-300"
                            >
                              -
                            </button>
                            <span className="w-8 text-center font-medium">{item.quantity}</span>
                            <button
                              onClick={() => handleQuantityChange(item.product.id, item.quantity + 1)}
                              className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 hover:bg-gray-300"
                            >
                              +
                            </button>
                            <button
                              onClick={() => removeItem(item.product.id)}
                              className="ml-4 text-red-600 hover:text-red-800"
                            >
                              Remove
                            </button>
                          </div>
                          <div className="ml-4 text-right">
                            <p className="text-sm font-medium text-gray-900">
                              ${item.total.toFixed(2)}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Order Summary */}
              <div className="lg:col-span-1">
                <div className="bg-white rounded-lg shadow">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h2 className="text-lg font-medium text-gray-900">Order Summary</h2>
                  </div>
                  <div className="px-6 py-4">
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Subtotal</span>
                        <span className="text-sm font-medium text-gray-900">
                          ${total.toFixed(2)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Tax</span>
                        <span className="text-sm font-medium text-gray-900">
                          ${(total * 0.08).toFixed(2)}
                        </span>
                      </div>
                      <div className="border-t border-gray-200 pt-2">
                        <div className="flex justify-between">
                          <span className="text-base font-medium text-gray-900">Total</span>
                          <span className="text-base font-medium text-gray-900">
                            ${(total * 1.08).toFixed(2)}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="mt-6">
                      <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
                        Special Instructions
                      </label>
                      <textarea
                        id="notes"
                        rows={3}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                        placeholder="Any special requests or notes..."
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                      />
                    </div>

                    {error && (
                      <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                        {error}
                      </div>
                    )}

                    <button
                      onClick={handlePlaceOrder}
                      disabled={loading || items.length === 0}
                      className="w-full mt-6 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white px-4 py-3 rounded-md font-medium"
                    >
                      {loading ? 'Placing Order...' : 'Place Order'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};