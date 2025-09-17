export interface Business {
  id: string;
  name: string;
  description?: string;
  address?: string;
  phone?: string;
  email?: string;
  business_type: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface BusinessCreate {
  name: string;
  description?: string;
  address?: string;
  phone?: string;
  email?: string;
  business_type?: string;
}

export interface Product {
  id: string;
  business_id: string;
  name: string;
  description?: string;
  price: number;
  category?: string;
  image_url?: string;
  is_available: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ProductCreate {
  business_id: string;
  name: string;
  description?: string;
  price: number;
  category?: string;
  image_url?: string;
}