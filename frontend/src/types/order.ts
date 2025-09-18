export interface OrderItem {
  id: string;
  order_id: string;
  product_id: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface OrderItemCreate {
  product_id: string;
  quantity: number;
  unit_price: number;
}

export interface Order {
  id: string;
  user_id: string;
  business_id: string;
  status: OrderStatus;
  total_amount: number;
  notes?: string;
  created_at: string;
  updated_at?: string;
  items: OrderItem[];
}

export interface OrderCreate {
  business_id: string;
  notes?: string;
  items: OrderItemCreate[];
}

export interface OrderUpdate {
  status?: string;
  notes?: string;
}

export enum OrderStatus {
  PENDING = "pending",
  CONFIRMED = "confirmed",
  PREPARING = "preparing",
  READY = "ready",
  DELIVERED = "delivered",
  CANCELLED = "cancelled"
}

export interface CartItem {
  product: {
    id: string;
    name: string;
    price: number;
    business_id: string;
    description?: string;
    image_url?: string;
  };
  quantity: number;
}