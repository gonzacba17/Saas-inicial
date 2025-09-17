export interface ProductSalesStats {
  product_id: string;
  product_name: string;
  total_quantity: number;
  total_revenue: number;
}

export interface BusinessAnalytics {
  business_id: string;
  business_name: string;
  total_orders: number;
  total_revenue: number;
  pending_orders: number;
  completed_orders: number;
  top_products: ProductSalesStats[];
}

export interface DateRangeStats {
  start_date: string;
  end_date: string;
  total_orders: number;
  total_revenue: number;
  average_order_value: number;
}

export interface DailySales {
  date: string;
  orders: number;
  revenue: number;
}