#!/usr/bin/env python3
"""
Script para verificar y resetear la contraseña del usuario admin
Cafeteria IA - SaaS Local Development

Este script:
1. Verifica si el usuario admin existe en la base de datos SQLite
2. Resetea su contraseña a "Admin1234!" con hash seguro usando passlib
3. Confirma que el usuario puede autenticarse correctamente
4. Proporciona información detallada para debugging

Autor: Sistema de setup automático
Fecha: 2025
"""

import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

# Agregar el directorio backend al PYTHONPATH
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def setup_environment():
    """Configurar el entorno Python correctamente"""
    print("🔧 Configurando entorno Python...")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("app"):
        print("❌ Error: Este script debe ejecutarse desde el directorio 'backend'")
        print("   Ejecute: cd backend && python reset_admin_password.py")
        sys.exit(1)
    
    # Verificar que existe el archivo de base de datos o .env.local
    if not os.path.exists("saas_cafeterias_local.db") and not os.path.exists(".env.local"):
        print("⚠️  Advertencia: No se encuentra base de datos ni .env.local")
        print("   Ejecute primero: python create_admin.py")
    
    print("✅ Entorno configurado correctamente")

def test_imports():
    """Verificar que todas las importaciones funcionen"""
    print("\n🔍 Verificando importaciones...")
    
    try:
        from app.core.config import settings
        print(f"✅ Config cargado - Base de datos: {settings.db_url}")
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        return False
    
    try:
        from app.db.db import User, UserRole, UserCRUD, get_db, create_tables
        print("✅ Modelos de base de datos importados")
    except Exception as e:
        print(f"❌ Error importando modelos: {e}")
        return False
    
    try:
        from app.services import get_password_hash, verify_password, authenticate_user
        print("✅ Servicios de autenticación importados")
    except Exception as e:
        print(f"❌ Error importando servicios: {e}")
        return False
    
    return True

def check_database_direct():
    """Verificar la base de datos SQLite directamente"""
    print("\n🔍 Verificando base de datos SQLite directamente...")
    
    db_path = "saas_cafeterias_local.db"
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar que existe la tabla users
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        if not cursor.fetchone():
            print("❌ Tabla 'users' no existe en la base de datos")
            conn.close()
            return False
        
        # Buscar usuario admin
        cursor.execute("SELECT id, email, username, role, is_active, is_superuser FROM users WHERE username = ? OR email = ?", 
                      ("admin", "admin@saas.test"))
        admin_user = cursor.fetchone()
        
        if admin_user:
            print("✅ Usuario admin encontrado en base de datos:")
            print(f"   ID: {admin_user[0]}")
            print(f"   Email: {admin_user[1]}")
            print(f"   Username: {admin_user[2]}")
            print(f"   Role: {admin_user[3]}")
            print(f"   Active: {admin_user[4]}")
            print(f"   Superuser: {admin_user[5]}")
        else:
            print("❌ Usuario admin NO encontrado en base de datos")
            
            # Mostrar todos los usuarios para debugging
            cursor.execute("SELECT email, username, role FROM users LIMIT 5")
            users = cursor.fetchall()
            if users:
                print("   Usuarios existentes:")
                for user in users:
                    print(f"     - {user[1]} ({user[0]}) - {user[2]}")
            else:
                print("   No hay usuarios en la base de datos")
        
        conn.close()
        return admin_user is not None
        
    except Exception as e:
        print(f"❌ Error accediendo a la base de datos: {e}")
        return False

def reset_admin_password():
    """Resetear la contraseña del usuario admin usando passlib"""
    print("\n🔑 Reseteando contraseña del usuario admin...")
    
    try:
        # Importar componentes necesarios
        from app.db.db import User, UserRole, UserCRUD, get_db, create_tables
        from app.services import get_password_hash, verify_password, authenticate_user, get_user_by_username, get_user_by_email
        from sqlalchemy.orm import Session
        
        # Crear tablas si no existen
        create_tables()
        
        # Obtener sesión de base de datos
        db_gen = get_db()
        db: Session = next(db_gen)
        
        # Buscar usuario admin
        admin_user = get_user_by_username(db, "admin")
        if not admin_user:
            admin_user = get_user_by_email(db, "admin@saas.test")
        
        if not admin_user:
            print("❌ Usuario admin no encontrado. Creando nuevo usuario admin...")
            
            # Crear usuario admin
            new_password_hash = get_password_hash("Admin1234!")
            admin_data = {
                "email": "admin@saas.test",
                "username": "admin",
                "hashed_password": new_password_hash,
                "role": UserRole.ADMIN,
                "is_active": True,
                "is_superuser": True
            }
            
            admin_user = UserCRUD.create(db, admin_data)
            print("✅ Usuario admin creado exitosamente")
            
        else:
            print("✅ Usuario admin encontrado. Reseteando contraseña...")
            
            # Resetear contraseña
            new_password_hash = get_password_hash("Admin1234!")
            admin_user.hashed_password = new_password_hash
            admin_user.is_active = True
            
            # Asegurar que tiene rol admin
            admin_user.role = UserRole.ADMIN
            admin_user.is_superuser = True
            
            db.commit()
            db.refresh(admin_user)
            print("✅ Contraseña reseteada exitosamente")
        
        # Verificar la nueva contraseña
        print("\n🧪 Verificando nueva contraseña...")
        password_valid = verify_password("Admin1234!", admin_user.hashed_password)
        
        if password_valid:
            print("✅ Verificación de contraseña exitosa")
        else:
            print("❌ Error en verificación de contraseña")
            db.close()
            return False
        
        # Probar autenticación completa
        print("\n🔐 Probando autenticación completa...")
        auth_user = authenticate_user(db, "admin", "Admin1234!")
        
        if auth_user:
            print("✅ Autenticación exitosa")
            print(f"   Usuario: {auth_user.username}")
            print(f"   Email: {auth_user.email}")
            print(f"   Role: {auth_user.role}")
            print(f"   Active: {auth_user.is_active}")
            print(f"   Superuser: {auth_user.is_superuser}")
        else:
            print("❌ Error en autenticación")
            db.close()
            return False
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error reseteando contraseña: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_password_hash():
    """Probar que el hashing de contraseñas funciona correctamente"""
    print("\n🧪 Probando sistema de hash de contraseñas...")
    
    try:
        from app.services import get_password_hash, verify_password
        
        test_password = "Admin1234!"
        
        # Generar hash
        hashed = get_password_hash(test_password)
        print(f"✅ Hash generado: {hashed[:50]}...")
        
        # Verificar hash
        is_valid = verify_password(test_password, hashed)
        if is_valid:
            print("✅ Verificación de hash exitosa")
        else:
            print("❌ Error en verificación de hash")
            return False
        
        # Verificar hash incorrecto
        is_invalid = verify_password("wrongpassword", hashed)
        if not is_invalid:
            print("✅ Rechazo de contraseña incorrecta exitoso")
        else:
            print("❌ Error: se aceptó contraseña incorrecta")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando hash: {e}")
        return False

def generate_test_commands():
    """Generar comandos de prueba para verificar el login"""
    print("\n📋 Comandos de prueba generados:")
    
    print("\n1. 🌐 Probar con cURL:")
    print('curl -X POST "http://localhost:8000/api/v1/auth/login" \\')
    print('     -H "Content-Type: application/x-www-form-urlencoded" \\')
    print('     -d "username=admin&password=Admin1234!"')
    
    print("\n2. 🔧 Probar con PowerShell (Windows):")
    print('$body = @{')
    print('    username = "admin"')
    print('    password = "Admin1234!"')
    print('}')
    print('Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Body $body')
    
    print("\n3. 📱 Credenciales para frontend/Postman:")
    print("   URL: http://localhost:8000/api/v1/auth/login")
    print("   Method: POST")
    print("   Content-Type: application/x-www-form-urlencoded")
    print("   Body:")
    print("     username: admin")
    print("     password: Admin1234!")
    
    print("\n4. 🧪 URLs de verificación:")
    print("   Health: http://localhost:8000/health")
    print("   API Docs: http://localhost:8000/docs")
    print("   OpenAPI: http://localhost:8000/api/v1/openapi.json")

def main():
    """Función principal del script"""
    print("🚀 Cafeteria IA - Reset de Contraseña Admin")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Configurar entorno
    setup_environment()
    
    # Verificar importaciones
    if not test_imports():
        print("\n❌ Error en importaciones. Verifica que:")
        print("   - Estés en el directorio 'backend'")
        print("   - El virtual environment esté activado")
        print("   - Las dependencias estén instaladas: pip install -r requirements.txt")
        sys.exit(1)
    
    # Verificar base de datos directamente
    check_database_direct()
    
    # Probar sistema de hash
    if not test_password_hash():
        print("\n❌ Error en sistema de hash de contraseñas")
        sys.exit(1)
    
    # Resetear contraseña del admin
    if not reset_admin_password():
        print("\n❌ Error reseteando contraseña del admin")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 RESET DE CONTRASEÑA COMPLETADO EXITOSAMENTE")
    print("=" * 50)
    
    print("\n👤 Credenciales del Admin:")
    print("   Username: admin")
    print("   Email: admin@saas.test")
    print("   Password: Admin1234!")
    print("   Role: admin")
    print("   Status: active")
    
    # Generar comandos de prueba
    generate_test_commands()
    
    print("\n📝 Próximos pasos:")
    print("1. Iniciar el backend: python -m uvicorn app.main:app --reload")
    print("2. Probar login con los comandos generados arriba")
    print("3. Si persisten problemas, verificar CORS y configuración de frontend")
    
    print("\n🔍 Si el login sigue fallando, revisar:")
    print("   - Backend corriendo en puerto 8000")
    print("   - CORS configurado para localhost:5173")
    print("   - Frontend .env tiene VITE_API_URL=http://localhost:8000")
    print("   - Usar 'admin' como username, NO el email")

if __name__ == "__main__":
    main()