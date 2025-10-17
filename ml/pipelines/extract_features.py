from typing import Dict, List, Any
import pandas as pd
from datetime import datetime


def extract_order_features(order_data: Dict[str, Any]) -> Dict[str, Any]:
    features = {
        'order_id': order_data.get('id'),
        'customer_id': order_data.get('customer_id'),
        'business_id': order_data.get('business_id'),
        'total_amount': order_data.get('total', 0.0),
        'item_count': len(order_data.get('items', [])),
        'created_at': order_data.get('created_at'),
        'status': order_data.get('status'),
    }
    
    if 'items' in order_data:
        features['avg_item_price'] = features['total_amount'] / max(features['item_count'], 1)
        features['product_categories'] = list(set([item.get('category') for item in order_data['items'] if item.get('category')]))
    
    return features


def extract_customer_features(customer_data: Dict[str, Any], orders: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    features = {
        'customer_id': customer_data.get('id'),
        'business_id': customer_data.get('business_id'),
        'registration_date': customer_data.get('created_at'),
        'total_orders': 0,
        'total_spent': 0.0,
        'avg_order_value': 0.0,
    }
    
    if orders:
        features['total_orders'] = len(orders)
        features['total_spent'] = sum(order.get('total', 0.0) for order in orders)
        features['avg_order_value'] = features['total_spent'] / max(features['total_orders'], 1)
        
        if features['total_orders'] > 1:
            dates = [datetime.fromisoformat(order['created_at'].replace('Z', '+00:00')) for order in orders if order.get('created_at')]
            if len(dates) > 1:
                date_diffs = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
                features['avg_days_between_orders'] = sum(date_diffs) / len(date_diffs)
    
    return features


def extract_product_features(product_data: Dict[str, Any], sales_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    features = {
        'product_id': product_data.get('id'),
        'business_id': product_data.get('business_id'),
        'name': product_data.get('name'),
        'category': product_data.get('category'),
        'price': product_data.get('price', 0.0),
        'stock': product_data.get('stock', 0),
        'total_sold': 0,
        'revenue': 0.0,
    }
    
    if sales_data:
        features['total_sold'] = sum(sale.get('quantity', 0) for sale in sales_data)
        features['revenue'] = sum(sale.get('quantity', 0) * sale.get('price', 0.0) for sale in sales_data)
    
    return features


def batch_extract_features(data_list: List[Dict[str, Any]], feature_extractor_fn) -> pd.DataFrame:
    features_list = [feature_extractor_fn(data) for data in data_list]
    return pd.DataFrame(features_list)
