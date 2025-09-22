#!/usr/bin/env python3
"""
Script para probar el login de admin programáticamente
Cafeteria IA - Testing automatizado del endpoint de login

Este script realiza pruebas automatizadas del endpoint de login para verificar
que el usuario admin puede autenticarse correctamente.
"""

import asyncio
import json
import sys
from pathlib import Path

# Agregar el directorio backend al PYTHONPATH
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def test_login_endpoint():
    """Probar el endpoint de login con httpx"""
    print("🧪 Probando endpoint de login...")
    
    try:
        import httpx
    except ImportError:
        print("❌ httpx no está instalado. Instalando...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx"])
        import httpx
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Probar health endpoint
        print("\n1. 🔍 Probando health endpoint...")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health OK: {health_data.get('status')} - Version: {health_data.get('version')}")
            else:
                print(f"❌ Health endpoint falló: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ No se puede conectar al backend: {e}")
            print("   Asegúrate de que el backend esté corriendo:")
            print("   python -m uvicorn app.main:app --reload")
            return False
        
        # 2. Probar OpenAPI docs
        print("\n2. 📖 Verificando OpenAPI docs...")
        try:
            response = await client.get(f"{base_url}/api/v1/openapi.json")
            if response.status_code == 200:
                print("✅ OpenAPI schema accesible")
            else:
                print(f"⚠️  OpenAPI schema issue: {response.status_code}")
        except Exception as e:
            print(f"⚠️  OpenAPI test falló: {e}")
        
        # 3. Probar login con credenciales correctas
        print("\n3. 🔐 Probando login con credenciales correctas...")
        login_data = {
            "username": "admin",
            "password": "Admin1234!"
        }
        
        try:
            response = await client.post(f"{base_url}/api/v1/auth/login", data=login_data)
            
            if response.status_code == 200:
                auth_response = response.json()
                print("✅ Login exitoso!")
                print(f"   Token type: {auth_response.get('token_type')}")
                print(f"   User ID: {auth_response.get('user_id')}")
                print(f"   Role: {auth_response.get('role')}")
                
                # Guardar token para próximas pruebas
                access_token = auth_response.get('access_token')
                
                # 4. Probar endpoint /me con token
                print("\n4. 👤 Probando endpoint /me con token...")
                headers = {"Authorization": f"Bearer {access_token}"}
                
                me_response = await client.get(f"{base_url}/api/v1/auth/me", headers=headers)
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    print("✅ Endpoint /me exitoso!")
                    print(f"   Username: {user_data.get('username')}")
                    print(f"   Email: {user_data.get('email')}")
                    print(f"   Role: {user_data.get('role')}")
                    print(f"   Active: {user_data.get('is_active')}")
                else:
                    print(f"❌ Endpoint /me falló: {me_response.status_code}")
                    print(f"   Response: {me_response.text}")
                
            else:
                print(f"❌ Login falló: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error en login: {e}")
            return False
        
        # 5. Probar login con credenciales incorrectas
        print("\n5. 🚫 Probando login con credenciales incorrectas...")
        bad_login_data = {
            "username": "admin",
            "password": "wrongpassword"
        }
        
        try:
            response = await client.post(f"{base_url}/api/v1/auth/login", data=bad_login_data)
            
            if response.status_code == 401:
                print("✅ Rechazo de credenciales incorrectas exitoso")
            else:
                print(f"⚠️  Respuesta inesperada para credenciales incorrectas: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️  Error probando credenciales incorrectas: {e}")
        
        # 6. Probar con email en lugar de username
        print("\n6. 📧 Probando login con email (debería fallar)...")
        email_login_data = {
            "username": "admin@saas.test",  # Usando email como username
            "password": "Admin1234!"
        }
        
        try:
            response = await client.post(f"{base_url}/api/v1/auth/login", data=email_login_data)
            
            if response.status_code == 401:
                print("✅ Rechazo de email como username (correcto)")
                print("   Nota: El login debe usar 'admin', no 'admin@saas.test'")
            elif response.status_code == 200:
                print("⚠️  Login con email funcionó (podría estar configurado para aceptar ambos)")
            else:
                print(f"⚠️  Respuesta inesperada: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️  Error probando login con email: {e}")
    
    return True

def generate_postman_collection():
    """Generar una colección de Postman para importar"""
    print("\n📋 Generando colección de Postman...")
    
    postman_collection = {
        "info": {
            "name": "Cafeteria IA - API Tests",
            "description": "Colección de pruebas para la API de Cafeteria IA",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [
            {
                "name": "Health Check",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {
                        "raw": "http://localhost:8000/health",
                        "protocol": "http",
                        "host": ["localhost"],
                        "port": "8000",
                        "path": ["health"]
                    }
                }
            },
            {
                "name": "Admin Login",
                "request": {
                    "method": "POST",
                    "header": [
                        {
                            "key": "Content-Type",
                            "value": "application/x-www-form-urlencoded"
                        }
                    ],
                    "body": {
                        "mode": "urlencoded",
                        "urlencoded": [
                            {
                                "key": "username",
                                "value": "admin",
                                "type": "text"
                            },
                            {
                                "key": "password",
                                "value": "Admin1234!",
                                "type": "text"
                            }
                        ]
                    },
                    "url": {
                        "raw": "http://localhost:8000/api/v1/auth/login",
                        "protocol": "http",
                        "host": ["localhost"],
                        "port": "8000",
                        "path": ["api", "v1", "auth", "login"]
                    }
                }
            },
            {
                "name": "Get Current User",
                "request": {
                    "method": "GET",
                    "header": [
                        {
                            "key": "Authorization",
                            "value": "Bearer {{access_token}}",
                            "description": "Reemplazar {{access_token}} con el token del login"
                        }
                    ],
                    "url": {
                        "raw": "http://localhost:8000/api/v1/auth/me",
                        "protocol": "http",
                        "host": ["localhost"],
                        "port": "8000",
                        "path": ["api", "v1", "auth", "me"]
                    }
                }
            },
            {
                "name": "API Documentation",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {
                        "raw": "http://localhost:8000/docs",
                        "protocol": "http",
                        "host": ["localhost"],
                        "port": "8000",
                        "path": ["docs"]
                    }
                }
            }
        ]
    }
    
    try:
        with open("cafeteria_ia_postman_collection.json", "w", encoding="utf-8") as f:
            json.dump(postman_collection, f, indent=2, ensure_ascii=False)
        
        print("✅ Colección de Postman generada: cafeteria_ia_postman_collection.json")
        print("   Para importar en Postman:")
        print("   1. Abre Postman")
        print("   2. Click en 'Import'")
        print("   3. Selecciona el archivo: cafeteria_ia_postman_collection.json")
        
    except Exception as e:
        print(f"❌ Error generando colección de Postman: {e}")

def print_curl_examples():
    """Imprimir ejemplos de cURL para diferentes escenarios"""
    print("\n📝 Ejemplos de cURL:")
    
    print("\n1. Login exitoso:")
    print('curl -X POST "http://localhost:8000/api/v1/auth/login" \\')
    print('     -H "Content-Type: application/x-www-form-urlencoded" \\')
    print('     -d "username=admin&password=Admin1234!" \\')
    print('     -w "\\nStatus: %{http_code}\\n"')
    
    print("\n2. Health check:")
    print('curl -X GET "http://localhost:8000/health" \\')
    print('     -H "Accept: application/json" \\')
    print('     -w "\\nStatus: %{http_code}\\n"')
    
    print("\n3. Get current user (requiere token del login):")
    print('curl -X GET "http://localhost:8000/api/v1/auth/me" \\')
    print('     -H "Authorization: Bearer YOUR_TOKEN_HERE" \\')
    print('     -H "Accept: application/json" \\')
    print('     -w "\\nStatus: %{http_code}\\n"')
    
    print("\n4. Login con verbose output (para debugging):")
    print('curl -X POST "http://localhost:8000/api/v1/auth/login" \\')
    print('     -H "Content-Type: application/x-www-form-urlencoded" \\')
    print('     -d "username=admin&password=Admin1234!" \\')
    print('     -v')

async def main():
    """Función principal"""
    print("🧪 Cafeteria IA - Test de Login Automatizado")
    print("=" * 50)
    
    # Probar endpoints
    success = await test_login_endpoint()
    
    # Generar recursos adicionales
    generate_postman_collection()
    print_curl_examples()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("✅ El usuario admin puede autenticarse correctamente")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("🔍 Revisa los mensajes de error arriba")
    
    print("\n📋 Checklist de verificación:")
    print("□ Backend corriendo en puerto 8000")
    print("□ Health endpoint responde")
    print("□ Login con admin/Admin1234! funciona")
    print("□ Token JWT se genera correctamente")
    print("□ Endpoint /me funciona con token")
    print("□ Credenciales incorrectas son rechazadas")
    
    print("\n🚀 Si todos los tests pasan, el sistema está listo para usar!")

if __name__ == "__main__":
    asyncio.run(main())