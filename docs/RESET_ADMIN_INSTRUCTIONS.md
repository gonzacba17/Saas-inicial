# 🔑 Cafeteria IA - Reset de Contraseña Admin

## 📋 Instrucciones para Windows PowerShell

### 🚀 Ejecución Rápida

```powershell
# Abrir PowerShell en el directorio del proyecto
cd "C:\wamp64\www\Saas-inicial\backend"

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Ejecutar script de reset
python reset_admin_password.py
```

### 📝 Paso a Paso Detallado

#### 1. Preparar el Entorno

```powershell
# Navegar al directorio del proyecto
cd "C:\wamp64\www\Saas-inicial"

# Entrar al directorio backend
cd backend

# Verificar que existe el entorno virtual
if (Test-Path "venv") {
    Write-Host "✅ Virtual environment encontrado" -ForegroundColor Green
} else {
    Write-Host "❌ Virtual environment no encontrado. Ejecute setup primero." -ForegroundColor Red
    exit
}

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Verificar que Python funciona
python --version
```

#### 2. Ejecutar Script de Reset

```powershell
# Ejecutar el script
python reset_admin_password.py
```

**Output esperado:**
```
🚀 Cafeteria IA - Reset de Contraseña Admin
==================================================
🔧 Configurando entorno Python...
✅ Entorno configurado correctamente

🔍 Verificando importaciones...
✅ Config cargado - Base de datos: sqlite:///./saas_cafeterias_local.db
✅ Modelos de base de datos importados
✅ Servicios de autenticación importados

🔍 Verificando base de datos SQLite directamente...
✅ Usuario admin encontrado en base de datos:
   ID: [uuid]
   Email: admin@saas.test
   Username: admin
   Role: admin
   Active: True
   Superuser: True

🧪 Probando sistema de hash de contraseñas...
✅ Hash generado: $2b$12$...
✅ Verificación de hash exitosa
✅ Rechazo de contraseña incorrecta exitoso

🔑 Reseteando contraseña del usuario admin...
✅ Usuario admin encontrado. Reseteando contraseña...
✅ Contraseña reseteada exitosamente

🧪 Verificando nueva contraseña...
✅ Verificación de contraseña exitosa

🔐 Probando autenticación completa...
✅ Autenticación exitosa
   Usuario: admin
   Email: admin@saas.test
   Role: UserRole.ADMIN
   Active: True
   Superuser: True

🎉 RESET DE CONTRASEÑA COMPLETADO EXITOSAMENTE
```

#### 3. Iniciar Backend

```powershell
# Iniciar el servidor backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Output esperado:**
```
INFO:     Will watch for changes in these directories: ['C:\\wamp64\\www\\Saas-inicial\\backend']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxx] using WatchFiles
INFO:     Started server process [xxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## 🧪 Testing del Login

### 1. Test con cURL (PowerShell)

```powershell
# Test básico de login
curl -X POST "http://localhost:8000/api/v1/auth/login" -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=Admin1234!"
```

**Response esperado:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user_id": "12345678-1234-5678-9012-123456789012",
  "role": "admin"
}
```

### 2. Test con PowerShell Invoke-RestMethod

```powershell
# Crear body de request
$loginBody = @{
    username = "admin"
    password = "Admin1234!"
}

# Ejecutar request
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Body $loginBody

# Mostrar resultado
$response | ConvertTo-Json -Depth 3
```

### 3. Test con Postman

**Configuración:**
- **URL:** `http://localhost:8000/api/v1/auth/login`
- **Method:** `POST`
- **Headers:** 
  ```
  Content-Type: application/x-www-form-urlencoded
  ```
- **Body (x-www-form-urlencoded):**
  ```
  username: admin
  password: Admin1234!
  ```

**Response exitoso (Status 200):**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "user_id": "uuid-here",
    "role": "admin"
}
```

### 4. Verificar API Health

```powershell
# Test de salud de la API
curl http://localhost:8000/health
```

**Response esperado:**
```json
{
    "status": "healthy",
    "version": "1.0.0",
    "environment": "development"
}
```

### 5. Verificar API Docs

- **URL:** http://localhost:8000/docs
- Debe cargar la interfaz Swagger UI sin errores

## 🔍 Troubleshooting

### ❌ Error: "ModuleNotFoundError"

**Causa:** Virtual environment no activado o dependencias faltantes

**Solución:**
```powershell
# Activar venv
.\venv\Scripts\Activate.ps1

# Reinstalar dependencias
pip install -r requirements.txt

# Verificar instalación específica
pip list | grep -i passlib
pip list | grep -i sqlalchemy
```

### ❌ Error: "Database locked" o "Permission denied"

**Causa:** Archivo de base de datos en uso o permisos incorrectos

**Solución:**
```powershell
# Detener cualquier proceso que use la DB
# Verificar procesos Python
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Eliminar archivo de DB y recrear (CUIDADO: esto borra datos)
Remove-Item "saas_cafeterias_local.db" -Force -ErrorAction SilentlyContinue
python reset_admin_password.py
```

### ❌ Error: "401 Unauthorized" en login

**Posibles causas y soluciones:**

1. **Backend no corriendo:**
   ```powershell
   # Verificar que el backend está corriendo
   curl http://localhost:8000/health
   ```

2. **CORS mal configurado:**
   - Verificar que `.env.local` contiene:
   ```env
   ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173
   ```

3. **Usando email en lugar de username:**
   - ✅ Correcto: `username=admin`
   - ❌ Incorrecto: `username=admin@saas.test`

4. **Frontend apunta a URL incorrecta:**
   - Verificar `frontend/.env`:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

### ❌ Error: "ValidationError" o "Schema error"

**Causa:** Problema en schemas o modelos

**Solución:**
```powershell
# Verificar importaciones
python -c "from app.schemas import User, Token; print('Schemas OK')"

# Verificar modelos
python -c "from app.db.db import User, UserRole; print('Models OK')"
```

### ❌ Frontend no se conecta al backend

**Verificaciones:**

1. **Backend corriendo en puerto correcto:**
   ```powershell
   netstat -an | findstr 8000
   ```

2. **Frontend configurado correctamente:**
   ```powershell
   # Verificar .env del frontend
   Get-Content frontend/.env
   ```

3. **CORS habilitado:**
   - El backend debe mostrar: `CORS middleware configured`

4. **Firewall/Antivirus:**
   - Temporalmente desactivar para pruebas
   - Agregar excepción para Python y Node.js

## 📱 Credenciales Finales

**Una vez completado el reset:**

- **Username:** `admin`
- **Email:** `admin@saas.test` 
- **Password:** `Admin1234!`
- **Role:** `admin`
- **Superuser:** `true`
- **Active:** `true`

## 🚀 Comandos de Inicio Rápido

```powershell
# Terminal 1 - Backend
cd "C:\wamp64\www\Saas-inicial\backend"
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 - Frontend (si es necesario)
cd "C:\wamp64\www\Saas-inicial\frontend"
npm run dev
```

## 📞 Verificación Final

Después de ejecutar todos los pasos:

1. ✅ Script de reset ejecutado sin errores
2. ✅ Backend iniciado correctamente
3. ✅ Login con cURL funciona
4. ✅ API docs accesible
5. ✅ Frontend puede autenticar (si aplica)

Si todos los checks pasan, el sistema está funcionando correctamente.