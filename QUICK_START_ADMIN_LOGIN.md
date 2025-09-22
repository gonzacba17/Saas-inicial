# ⚡ Cafeteria IA - Quick Start: Admin Login Fix

## 🚀 Solución Rápida (2 minutos)

```powershell
# 1. Abrir PowerShell en el directorio del proyecto
cd "C:\wamp64\www\Saas-inicial\backend"

# 2. Activar entorno virtual
.\venv\Scripts\Activate.ps1

# 3. Resetear contraseña admin
python reset_admin_password.py

# 4. Iniciar backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 5. Probar login (en otra terminal)
curl -X POST "http://localhost:8000/api/v1/auth/login" -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=Admin1234!"
```

## 🎯 Credenciales Confirmadas

- **Username:** `admin` (NO usar email)
- **Password:** `Admin1234!`
- **URL Login:** `http://localhost:8000/api/v1/auth/login`
- **Method:** `POST`
- **Content-Type:** `application/x-www-form-urlencoded`

## 🧪 Testing Automático

```powershell
# Ejecutar tests automatizados (backend debe estar corriendo)
python test_login.py
```

## 📱 Guías Detalladas

- **Setup completo:** `RESET_ADMIN_INSTRUCTIONS.md`
- **Troubleshooting:** Ver sección "🔍 Troubleshooting" en el archivo de instrucciones

## 🔍 Verificación Rápida

Si el login falla, verificar en orden:

1. **Backend corriendo:** `curl http://localhost:8000/health`
2. **Usuario existe:** `python reset_admin_password.py`
3. **CORS configurado:** Verificar `.env.local` tiene `ALLOWED_ORIGINS`
4. **Usar username correcto:** `admin` (no `admin@saas.test`)

## ⚠️ Problemas Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `401 Unauthorized` | Username incorrecto | Usar `admin`, no email |
| `Connection refused` | Backend no corriendo | Iniciar con `uvicorn` |
| `ModuleNotFoundError` | Venv no activado | `.\venv\Scripts\Activate.ps1` |
| `CORS error` | Frontend mal configurado | Verificar `ALLOWED_ORIGINS` |

## 🎉 Success Response

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user_id": "uuid-here",
  "role": "admin"
}
```

## 📞 Contacto de Soporte

Si persisten problemas después de seguir esta guía:
1. Ejecutar `python reset_admin_password.py` y copiar output completo
2. Ejecutar `python test_login.py` y copiar resultados
3. Verificar logs del backend durante el intento de login