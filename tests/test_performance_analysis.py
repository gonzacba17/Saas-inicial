"""
Performance analysis test suite for critical endpoints.
Measures response times and identifies bottlenecks in the SaaS platform.
"""
import pytest
import requests
import time
import statistics
import json
from typing import Dict, List, Tuple
from datetime import datetime


class PerformanceAnalyzer:
    """Comprehensive performance testing for critical endpoints."""
    
    BASE_URL = "http://localhost:8000"
    
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.business_id = None
        self.product_id = None
        self.performance_data = {}
        self.slow_endpoints = []
        self.critical_thresholds = {
            'fast': 100,      # < 100ms
            'acceptable': 500, # < 500ms
            'slow': 1000,     # < 1000ms
            'critical': 2000  # > 2000ms is critical
        }
    
    def _measure_request(self, method: str, endpoint: str, headers: Dict = None, 
                        json_data: Dict = None, data: Dict = None, 
                        iterations: int = 5) -> Dict:
        """Measure request performance with multiple iterations."""
        times = []
        errors = 0
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                url = f"{self.BASE_URL}{endpoint}"
                
                if method.upper() == "GET":
                    response = requests.get(url, headers=headers, timeout=10)
                elif method.upper() == "POST":
                    if json_data:
                        response = requests.post(url, headers=headers, json=json_data, timeout=10)
                    else:
                        response = requests.post(url, headers=headers, data=data, timeout=10)
                elif method.upper() == "PUT":
                    response = requests.put(url, headers=headers, json=json_data, timeout=10)
                elif method.upper() == "DELETE":
                    response = requests.delete(url, headers=headers, timeout=10)
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                
                if response.status_code >= 400:
                    errors += 1
                else:
                    times.append(response_time)
                    
            except Exception as e:
                errors += 1
                print(f"Error in iteration {i+1}: {e}")
        
        if not times:
            return {
                'endpoint': f"{method} {endpoint}",
                'avg': 0,
                'min': 0,
                'max': 0,
                'median': 0,
                'std_dev': 0,
                'errors': errors,
                'success_rate': 0,
                'status': 'FAILED'
            }
        
        avg_time = statistics.mean(times)
        
        # Determine performance status
        if avg_time < self.critical_thresholds['fast']:
            status = '⚡ FAST'
        elif avg_time < self.critical_thresholds['acceptable']:
            status = '🟡 ACCEPTABLE'
        elif avg_time < self.critical_thresholds['slow']:
            status = '🟠 SLOW'
        else:
            status = '🔴 CRITICAL'
            
        result = {
            'endpoint': f"{method} {endpoint}",
            'avg': round(avg_time, 2),
            'min': round(min(times), 2),
            'max': round(max(times), 2),
            'median': round(statistics.median(times), 2),
            'std_dev': round(statistics.stdev(times) if len(times) > 1 else 0, 2),
            'errors': errors,
            'success_rate': round((len(times) / iterations) * 100, 1),
            'status': status,
            'iterations': iterations
        }
        
        # Track slow endpoints
        if avg_time > self.critical_thresholds['acceptable']:
            self.slow_endpoints.append(result)
            
        return result
    
    def test_01_setup_authentication(self):
        """Setup admin and user tokens for performance testing."""
        # Admin login
        admin_data = {"username": "admin", "password": "Admin1234!"}
        try:
            response = requests.post(f"{self.BASE_URL}/api/v1/auth/login", data=admin_data, timeout=10)
            if response.status_code == 200:
                self.admin_token = response.json()["access_token"]
        except Exception as e:
            pytest.skip(f"Could not authenticate admin: {e}")
        
        # Create and login regular user
        user_data = {
            "email": "perftest@example.com",
            "username": "perfuser",
            "password": "PerfTest123!"
        }
        try:
            requests.post(f"{self.BASE_URL}/api/v1/auth/register", json=user_data, timeout=10)
            login_data = {"username": "perfuser", "password": "PerfTest123!"}
            response = requests.post(f"{self.BASE_URL}/api/v1/auth/login", data=login_data, timeout=10)
            if response.status_code == 200:
                self.user_token = response.json()["access_token"]
        except Exception:
            pass  # User might already exist
    
    def test_02_authentication_performance(self):
        """Test authentication endpoint performance."""
        print("\n🔐 AUTHENTICATION PERFORMANCE ANALYSIS")
        print("=" * 60)
        
        # Test login performance
        login_data = {"username": "admin", "password": "Admin1234!"}
        result = self._measure_request("POST", "/api/v1/auth/login", data=login_data, iterations=10)
        self.performance_data['auth_login'] = result
        print(f"Login: {result['avg']}ms avg ({result['status']})")
        
        # Test /me endpoint performance
        if self.admin_token:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            result = self._measure_request("GET", "/api/v1/auth/me", headers=headers, iterations=10)
            self.performance_data['auth_me'] = result
            print(f"/me: {result['avg']}ms avg ({result['status']})")
        
        # Test token refresh performance
        if self.admin_token:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            result = self._measure_request("POST", "/api/v1/auth/refresh", headers=headers, iterations=5)
            self.performance_data['auth_refresh'] = result
            print(f"Refresh: {result['avg']}ms avg ({result['status']})")
    
    def test_03_business_crud_performance(self):
        """Test business CRUD operations performance."""
        print("\n🏢 BUSINESS CRUD PERFORMANCE ANALYSIS")
        print("=" * 60)
        
        if not self.admin_token:
            pytest.skip("Admin token not available")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test business creation
        business_data = {
            "name": "Performance Test Business",
            "description": "Business for performance testing",
            "business_type": "restaurant"
        }
        result = self._measure_request("POST", "/api/v1/businesses", headers=headers, 
                                     json_data=business_data, iterations=5)
        self.performance_data['business_create'] = result
        print(f"Create Business: {result['avg']}ms avg ({result['status']})")
        
        # Get business ID for other tests
        try:
            response = requests.post(f"{self.BASE_URL}/api/v1/businesses", 
                                   headers=headers, json=business_data, timeout=10)
            if response.status_code in [200, 201]:
                self.business_id = response.json()["id"]
        except Exception:
            pass
        
        # Test business listing
        result = self._measure_request("GET", "/api/v1/businesses", headers=headers, iterations=10)
        self.performance_data['business_list'] = result
        print(f"List Businesses: {result['avg']}ms avg ({result['status']})")
        
        # Test business retrieval
        if self.business_id:
            result = self._measure_request("GET", f"/api/v1/businesses/{self.business_id}", 
                                         headers=headers, iterations=10)
            self.performance_data['business_get'] = result
            print(f"Get Business: {result['avg']}ms avg ({result['status']})")
            
            # Test business update
            update_data = {"description": "Updated description for performance test"}
            result = self._measure_request("PUT", f"/api/v1/businesses/{self.business_id}", 
                                         headers=headers, json_data=update_data, iterations=5)
            self.performance_data['business_update'] = result
            print(f"Update Business: {result['avg']}ms avg ({result['status']})")
    
    def test_04_product_crud_performance(self):
        """Test product CRUD operations performance."""
        print("\n📦 PRODUCT CRUD PERFORMANCE ANALYSIS")
        print("=" * 60)
        
        if not self.admin_token or not self.business_id:
            pytest.skip("Admin token or business ID not available")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test product creation
        product_data = {
            "name": "Performance Test Product",
            "description": "Product for performance testing",
            "price": 9.99,
            "category": "test"
        }
        result = self._measure_request("POST", f"/api/v1/businesses/{self.business_id}/products", 
                                     headers=headers, json_data=product_data, iterations=5)
        self.performance_data['product_create'] = result
        print(f"Create Product: {result['avg']}ms avg ({result['status']})")
        
        # Get product ID for other tests
        try:
            response = requests.post(f"{self.BASE_URL}/api/v1/businesses/{self.business_id}/products", 
                                   headers=headers, json=product_data, timeout=10)
            if response.status_code in [200, 201]:
                self.product_id = response.json()["id"]
        except Exception:
            pass
        
        # Test product listing
        result = self._measure_request("GET", f"/api/v1/businesses/{self.business_id}/products", 
                                     headers=headers, iterations=10)
        self.performance_data['product_list'] = result
        print(f"List Products: {result['avg']}ms avg ({result['status']})")
        
        # Test product retrieval
        if self.product_id:
            result = self._measure_request("GET", f"/api/v1/businesses/{self.business_id}/products/{self.product_id}", 
                                         headers=headers, iterations=10)
            self.performance_data['product_get'] = result
            print(f"Get Product: {result['avg']}ms avg ({result['status']})")
            
            # Test product update
            update_data = {"price": 12.99, "description": "Updated product for performance test"}
            result = self._measure_request("PUT", f"/api/v1/businesses/{self.business_id}/products/{self.product_id}", 
                                         headers=headers, json_data=update_data, iterations=5)
            self.performance_data['product_update'] = result
            print(f"Update Product: {result['avg']}ms avg ({result['status']})")
    
    def test_05_user_operations_performance(self):
        """Test user operations performance."""
        print("\n👤 USER OPERATIONS PERFORMANCE ANALYSIS")
        print("=" * 60)
        
        if not self.admin_token:
            pytest.skip("Admin token not available")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test user listing (admin only)
        result = self._measure_request("GET", "/api/v1/users/", headers=headers, iterations=10)
        self.performance_data['user_list'] = result
        print(f"List Users: {result['avg']}ms avg ({result['status']})")
        
        # Test user registration
        user_data = {
            "email": f"perftest{int(time.time())}@example.com",
            "username": f"perfuser{int(time.time())}",
            "password": "PerfTest123!"
        }
        result = self._measure_request("POST", "/api/v1/auth/register", json_data=user_data, iterations=3)
        self.performance_data['user_register'] = result
        print(f"Register User: {result['avg']}ms avg ({result['status']})")
    
    def test_06_generate_performance_report(self):
        """Generate comprehensive performance report."""
        print("\n📊 COMPREHENSIVE PERFORMANCE REPORT")
        print("=" * 80)
        
        if not self.performance_data:
            pytest.skip("No performance data collected")
        
        # Summary statistics
        all_times = [data['avg'] for data in self.performance_data.values() if data['avg'] > 0]
        if all_times:
            print(f"Overall Performance Metrics:")
            print(f"  Average Response Time: {statistics.mean(all_times):.2f}ms")
            print(f"  Fastest Endpoint: {min(all_times):.2f}ms")
            print(f"  Slowest Endpoint: {max(all_times):.2f}ms")
            print(f"  Standard Deviation: {statistics.stdev(all_times):.2f}ms")
        
        print(f"\nDetailed Endpoint Performance:")
        print("-" * 80)
        print(f"{'Endpoint':<35} {'Avg (ms)':<10} {'Min':<8} {'Max':<8} {'Status':<12}")
        print("-" * 80)
        
        for operation, data in self.performance_data.items():
            if data['avg'] > 0:
                print(f"{data['endpoint']:<35} {data['avg']:<10} {data['min']:<8} {data['max']:<8} {data['status']:<12}")
        
        # Slow endpoints analysis
        if self.slow_endpoints:
            print(f"\n🐌 SLOW ENDPOINTS (>{self.critical_thresholds['acceptable']}ms):")
            print("-" * 60)
            for endpoint in self.slow_endpoints:
                print(f"  {endpoint['endpoint']}: {endpoint['avg']}ms avg")
                print(f"    Recommendation: Optimize database queries or add caching")
        else:
            print(f"\n✅ All endpoints performing well (< {self.critical_thresholds['acceptable']}ms)")
        
        # Performance recommendations
        print(f"\n💡 PERFORMANCE OPTIMIZATION RECOMMENDATIONS:")
        print("-" * 60)
        
        critical_endpoints = [ep for ep in self.performance_data.values() 
                            if ep['avg'] > self.critical_thresholds['slow']]
        
        if critical_endpoints:
            print("🔴 CRITICAL - Immediate attention required:")
            for ep in critical_endpoints:
                print(f"  - {ep['endpoint']}: {ep['avg']}ms")
                print(f"    • Add database indexing")
                print(f"    • Implement Redis caching")
                print(f"    • Consider query optimization")
        
        slow_endpoints = [ep for ep in self.performance_data.values() 
                         if self.critical_thresholds['acceptable'] < ep['avg'] <= self.critical_thresholds['slow']]
        
        if slow_endpoints:
            print("🟡 MODERATE - Should be optimized:")
            for ep in slow_endpoints:
                print(f"  - {ep['endpoint']}: {ep['avg']}ms")
                print(f"    • Consider adding pagination")
                print(f"    • Review SQL query efficiency")
        
        # Save performance data for documentation
        self._save_performance_data()
    
    def _save_performance_data(self):
        """Save performance data to JSON for documentation."""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'performance_data': self.performance_data,
            'slow_endpoints': self.slow_endpoints,
            'thresholds': self.critical_thresholds,
            'summary': {
                'total_endpoints_tested': len(self.performance_data),
                'slow_endpoints_count': len(self.slow_endpoints),
                'average_response_time': statistics.mean([d['avg'] for d in self.performance_data.values() if d['avg'] > 0]) if self.performance_data else 0
            }
        }
        
        try:
            with open('/mnt/c/wamp64/www/Saas-inicial/performance_report.json', 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"\n📄 Performance report saved to: performance_report.json")
        except Exception as e:
            print(f"Could not save performance report: {e}")


def test_run_performance_analysis():
    """Run complete performance analysis."""
    analyzer = PerformanceAnalyzer()
    
    # Check if backend is running
    try:
        response = requests.get(f"{analyzer.BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            pytest.skip("Backend is not running")
    except:
        pytest.skip("Backend is not accessible. Start with: cd backend && python -m uvicorn app.main:app --reload")
    
    # Run all performance tests
    test_methods = [
        analyzer.test_01_setup_authentication,
        analyzer.test_02_authentication_performance,
        analyzer.test_03_business_crud_performance,
        analyzer.test_04_product_crud_performance,
        analyzer.test_05_user_operations_performance,
        analyzer.test_06_generate_performance_report,
    ]
    
    print("\n🚀 STARTING COMPREHENSIVE PERFORMANCE ANALYSIS")
    print("=" * 80)
    
    for test_method in test_methods:
        try:
            test_method()
        except pytest.skip.Exception as e:
            print(f"⏭️  Skipped {test_method.__name__}: {e}")
        except Exception as e:
            print(f"❌ Error in {test_method.__name__}: {e}")


if __name__ == "__main__":
    test_run_performance_analysis()