#!/usr/bin/env python3
"""
Script para crear usuario administrador en Cafeteria IA
Usa el mismo sistema de hashing que el resto de la aplicación
"""

import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import text

# Añadir el directorio actual al path para importar módulos de la app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.db.session import SessionLocal, engine
from app.db.models import User
from app.services.auth import get_password_hash, get_user_by_email, get_user_by_username


def create_admin_user():
    """
    Crea el usuario administrador si no existe
    """
    # Datos del administrador
    admin_data = {
        "email": "admin@example.com",
        "username": "admin", 
        "password": "TuPassword123",  # Se hasheará automáticamente
        "full_name": "Administrador",
        "is_active": True,
        "is_superuser": True
    }
    
    print("🔧 Iniciando creación de usuario administrador...")
    print(f"📊 Conectando a: {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")
    
    # Crear sesión de base de datos
    db: Session = SessionLocal()
    
    try:
        # Verificar conexión a la base de datos
        db.execute(text("SELECT 1"))
        print("✅ Conexión a la base de datos establecida")
        
        # Verificar si el usuario ya existe por email
        existing_user_email = get_user_by_email(db, admin_data["email"])
        if existing_user_email:
            print(f"⚠️  El usuario con email {admin_data['email']} ya existe")
            print(f"   ID: {existing_user_email.id}")
            print(f"   Username: {existing_user_email.username}")
            print(f"   Es superusuario: {existing_user_email.is_superuser}")
            return existing_user_email
        
        # Verificar si el usuario ya existe por username
        existing_user_username = get_user_by_username(db, admin_data["username"])
        if existing_user_username:
            print(f"⚠️  El usuario con username {admin_data['username']} ya existe")
            print(f"   ID: {existing_user_username.id}")
            print(f"   Email: {existing_user_username.email}")
            print(f"   Es superusuario: {existing_user_username.is_superuser}")
            return existing_user_username
        
        # Hashear la contraseña usando la misma función que la app
        hashed_password = get_password_hash(admin_data["password"])
        print("🔐 Contraseña hasheada correctamente")
        
        # Crear el nuevo usuario administrador
        new_admin = User(
            email=admin_data["email"],
            username=admin_data["username"],
            hashed_password=hashed_password,
            is_active=admin_data["is_active"],
            is_superuser=admin_data["is_superuser"]
        )
        
        # Agregar a la base de datos
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        
        print("✅ Usuario administrador creado exitosamente!")
        print(f"   📧 Email: {new_admin.email}")
        print(f"   👤 Username: {new_admin.username}")
        print(f"   🆔 ID: {new_admin.id}")
        print(f"   🔑 Es superusuario: {new_admin.is_superuser}")
        print(f"   ✅ Está activo: {new_admin.is_active}")
        print(f"   📅 Creado en: {new_admin.created_at}")
        
        return new_admin
        
    except Exception as e:
        print(f"❌ Error al crear el usuario administrador: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def verify_admin_login():
    """
    Verifica que el usuario administrador puede hacer login
    """
    print("\n🔍 Verificando credenciales de login...")
    
    from app.services.auth import authenticate_user
    
    db: Session = SessionLocal()
    try:
        # Intentar autenticar con las credenciales
        user = authenticate_user(db, "admin", "TuPassword123")
        
        if user:
            print("✅ Login verificado correctamente!")
            print(f"   Usuario autenticado: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Es superusuario: {user.is_superuser}")
            return True
        else:
            print("❌ Error: No se pudo autenticar al usuario")
            return False
            
    except Exception as e:
        print(f"❌ Error al verificar login: {e}")
        return False
    finally:
        db.close()


def main():
    """
    Función principal del script
    """
    print("=" * 60)
    print("     CREADOR DE USUARIO ADMINISTRADOR")
    print("           Cafeteria IA - SaaS")
    print("=" * 60)
    
    try:
        # Crear el usuario administrador
        admin_user = create_admin_user()
        
        # Verificar que puede hacer login
        login_success = verify_admin_login()
        
        print("\n" + "=" * 60)
        print("📋 RESUMEN:")
        print(f"   ✅ Usuario creado: {admin_user.email}")
        print(f"   ✅ Login verificado: {'Sí' if login_success else 'No'}")
        print("\n🎯 CREDENCIALES PARA EL FRONTEND:")
        print("   Username: admin")
        print("   Password: TuPassword123")
        print("   URL Login: http://localhost:8000/api/v1/auth/login")
        print("=" * 60)
        
        return admin_user
        
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        print("💡 Posibles soluciones:")
        print("   1. Verificar que PostgreSQL esté corriendo")
        print("   2. Verificar que la base de datos existe")
        print("   3. Verificar credenciales en .env")
        print("   4. Ejecutar migraciones: alembic upgrade head")
        sys.exit(1)


if __name__ == "__main__":
    main()