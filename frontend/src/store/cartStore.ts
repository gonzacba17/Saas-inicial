import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Product {
  id: string;
  name: string;
  price: number;
  cafe_id: string;
  description?: string;
  image_url?: string;
}

interface CartItem {
  product: Product;
  quantity: number;
  total: number;
}

interface CartState {
  items: CartItem[];
  total: number;
  cafe_id: string | null;
  
  // Actions
  addItem: (product: Product, quantity?: number) => void;
  removeItem: (productId: string) => void;
  updateQuantity: (productId: string, quantity: number) => void;
  clearCart: () => void;
  setCafe: (cafeId: string) => void;
  getItemCount: () => number;
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],
      total: 0,
      cafe_id: null,
      
      addItem: (product: Product, quantity = 1) => {
        const state = get();
        
        // Check if item already exists
        const existingItemIndex = state.items.findIndex(
          item => item.product.id === product.id
        );
        
        let newItems: CartItem[];
        
        if (existingItemIndex >= 0) {
          // Update existing item
          newItems = state.items.map((item, index) => {
            if (index === existingItemIndex) {
              const newQuantity = item.quantity + quantity;
              return {
                ...item,
                quantity: newQuantity,
                total: newQuantity * product.price,
              };
            }
            return item;
          });
        } else {
          // Add new item
          const newItem: CartItem = {
            product,
            quantity,
            total: quantity * product.price,
          };
          newItems = [...state.items, newItem];
        }
        
        const newTotal = newItems.reduce((sum, item) => sum + item.total, 0);
        
        set({
          items: newItems,
          total: newTotal,
          cafe_id: product.cafe_id,
        });
      },
      
      removeItem: (productId: string) => {
        const state = get();
        const newItems = state.items.filter(item => item.product.id !== productId);
        const newTotal = newItems.reduce((sum, item) => sum + item.total, 0);
        
        set({
          items: newItems,
          total: newTotal,
          cafe_id: newItems.length > 0 ? state.cafe_id : null,
        });
      },
      
      updateQuantity: (productId: string, quantity: number) => {
        if (quantity <= 0) {
          get().removeItem(productId);
          return;
        }
        
        const state = get();
        const newItems = state.items.map(item => {
          if (item.product.id === productId) {
            return {
              ...item,
              quantity,
              total: quantity * item.product.price,
            };
          }
          return item;
        });
        
        const newTotal = newItems.reduce((sum, item) => sum + item.total, 0);
        
        set({
          items: newItems,
          total: newTotal,
        });
      },
      
      clearCart: () => {
        set({
          items: [],
          total: 0,
          cafe_id: null,
        });
      },
      
      setCafe: (cafeId: string) => {
        set({ cafe_id: cafeId });
      },
      
      getItemCount: () => {
        const state = get();
        return state.items.reduce((count, item) => count + item.quantity, 0);
      },
    }),
    {
      name: 'cart-storage',
      partialize: (state) => ({
        items: state.items,
        total: state.total,
        cafe_id: state.cafe_id,
      }),
    }
  )
);