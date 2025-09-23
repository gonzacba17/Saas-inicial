#!/usr/bin/env python3
"""
Script de validación de integraciones del sistema SaaS Cafeterías.
Ejecuta verificaciones básicas de conectividad y configuración.
"""

import os
import sys
import asyncio
import httpx
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "backend"))

try:
    from app.services_directory.payment_service import PaymentService
    from app.services_directory.ai_service import AIService
    from app.services_directory.cache_service import CacheService
except ImportError as e:
    print(f"❌ Error importing services: {e}")
    print("Ensure you're running from the project root and dependencies are installed")
    sys.exit(1)


async def validate_api_health():
    """Validate API health endpoint."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✅ API Health: OK")
                return True
            else:
                print(f"❌ API Health: Failed (status: {response.status_code})")
                return False
    except Exception as e:
        print(f"❌ API Health: Connection failed - {e}")
        return False


def validate_environment_variables():
    """Validate required environment variables."""
    required_vars = [
        "SECRET_KEY",
        "DATABASE_URL"
    ]
    
    optional_vars = [
        "MERCADOPAGO_ACCESS_TOKEN",
        "OPENAI_API_KEY", 
        "REDIS_URL"
    ]
    
    print("🔍 Validating Environment Variables...")
    
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    if missing_required:
        print(f"❌ Missing required variables: {', '.join(missing_required)}")
        return False
    else:
        print("✅ Required variables: OK")
    
    missing_optional = []
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_optional:
        print(f"⚠️  Missing optional variables: {', '.join(missing_optional)}")
    else:
        print("✅ Optional variables: All present")
    
    return True


def validate_payment_service():
    """Validate MercadoPago integration."""
    print("💳 Validating Payment Service...")
    
    try:
        payment_service = PaymentService()
        
        # Test configuration
        if hasattr(payment_service, 'is_configured'):
            if payment_service.is_configured():
                print("✅ Payment Service: Configured")
                return True
            else:
                print("⚠️  Payment Service: Not configured (using mock)")
                return True
        else:
            print("✅ Payment Service: Available")
            return True
            
    except Exception as e:
        print(f"❌ Payment Service: Error - {e}")
        return False


def validate_ai_service():
    """Validate OpenAI integration."""
    print("🤖 Validating AI Service...")
    
    try:
        ai_service = AIService()
        
        # Basic initialization test
        if hasattr(ai_service, 'client'):
            print("✅ AI Service: Initialized")
            return True
        else:
            print("⚠️  AI Service: Client not available")
            return False
            
    except Exception as e:
        print(f"❌ AI Service: Error - {e}")
        return False


def validate_cache_service():
    """Validate Redis/Cache integration."""
    print("🗄️  Validating Cache Service...")
    
    try:
        cache_service = CacheService()
        
        # Test basic operation
        test_key = "validation_test"
        test_value = "test_data"
        
        cache_service.set(test_key, test_value)
        retrieved = cache_service.get(test_key)
        
        if retrieved == test_value:
            print("✅ Cache Service: Working")
            cache_service.delete(test_key)  # Cleanup
            return True
        else:
            print("❌ Cache Service: Data integrity issue")
            return False
            
    except Exception as e:
        print(f"❌ Cache Service: Error - {e}")
        return False


def validate_docker_services():
    """Validate Docker services status."""
    print("🐳 Validating Docker Services...")
    
    import subprocess
    
    try:
        # Check if docker-compose is running
        result = subprocess.run(
            ["docker-compose", "ps", "--services", "--filter", "status=running"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode == 0:
            running_services = result.stdout.strip().split('\n') if result.stdout.strip() else []
            if running_services:
                print(f"✅ Docker Services: {len(running_services)} services running")
                for service in running_services:
                    print(f"  - {service}")
                return True
            else:
                print("⚠️  Docker Services: No services detected")
                return False
        else:
            print("❌ Docker Services: docker-compose command failed")
            return False
            
    except FileNotFoundError:
        print("⚠️  Docker Services: docker-compose not found")
        return False
    except Exception as e:
        print(f"❌ Docker Services: Error - {e}")
        return False


async def main():
    """Run all validation checks."""
    print("🚀 SaaS Cafeterías - Integration Validation")
    print("=" * 50)
    
    validations = [
        ("Environment Variables", validate_environment_variables),
        ("Payment Service", validate_payment_service),
        ("AI Service", validate_ai_service),
        ("Cache Service", validate_cache_service),
        ("Docker Services", validate_docker_services),
        ("API Health", validate_api_health),
    ]
    
    results = {}
    
    for name, validation_func in validations:
        print(f"\n📋 {name}")
        print("-" * 30)
        
        try:
            if asyncio.iscoroutinefunction(validation_func):
                result = await validation_func()
            else:
                result = validation_func()
            results[name] = result
        except Exception as e:
            print(f"❌ {name}: Unexpected error - {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:<25} {status}")
    
    print(f"\nResult: {passed}/{total} validations passed")
    
    if passed == total:
        print("🎉 All validations passed! System is ready.")
        return 0
    else:
        print(f"⚠️  {total - passed} validation(s) failed. Check configuration.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)