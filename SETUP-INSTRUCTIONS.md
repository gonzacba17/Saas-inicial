# 🚀 INSTRUCCIONES DE CONFIGURACIÓN - CAFETERIA IA

## ✅ SOLUCIÓN COMPLETA LISTA PARA USAR

Este proyecto ha sido configurado con scripts automatizados que solucionan todos los problemas identificados:

- ✅ Migraciones de Alembic ejecutándose correctamente
- ✅ Usuario administrador creado automáticamente  
- ✅ Login API funcionando con access_token
- ✅ Scripts .bat funcionando desde PowerShell
- ✅ Frontend compilando sin errores PostCSS/Babel

---

## 🎯 CONFIGURACIÓN INICIAL (EJECUTAR UNA SOLA VEZ)

### **OPCIÓN 1: Script PowerShell (RECOMENDADO)**
```powershell
# Abrir PowerShell como Administrador en el directorio del proyecto
.\setup-complete.ps1
```

### **OPCIÓN 2: Script .bat (ALTERNATIVO)**
```cmd
# Doble clic o desde CMD
setup-complete.bat
```

### **OPCIÓN 3: Por pasos (MANUAL)**
```powershell
# 1. Solucionar problemas de Windows
.\fix-windows-issues.ps1

# 2. Configuración completa
.\setup-complete.ps1

# 3. Solo migraciones (si hay problemas)
.\setup-complete.ps1 -OnlyMigrations

# 4. Solo crear admin (si hay problemas)
.\setup-complete.ps1 -OnlyAdmin
```

---

## 🏃‍♂️ USO DIARIO - INICIAR SERVIDORES

### **Iniciar Backend y Frontend juntos:**
```powershell
.\start-all.ps1          # PowerShell
# o
start-all.bat           # Doble clic
```

### **Iniciar por separado:**
```powershell
# Backend (Puerto 8000)
.\start-backend.ps1

# Frontend (Puerto 5173)  
.\start-frontend.ps1
```

---

## 🔑 CREDENCIALES DE ADMINISTRADOR

```json
{
  "username": "admin",
  "password": "TuPassword123"
}
```

---

## 🌐 URLs DE LA APLICACIÓN

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend** | http://localhost:5173 | Aplicación React |
| **Backend** | http://localhost:8000 | API FastAPI |
| **API Docs** | http://localhost:8000/docs | Documentación Swagger |
| **API Redoc** | http://localhost:8000/redoc | Documentación ReDoc |

---

## 🧪 PROBAR EL LOGIN

### **Con cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=TuPassword123"
```

### **Respuesta esperada:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## 🛠️ SOLUCIÓN DE PROBLEMAS

### **Error: "no existe la relación users"**
```powershell
# Ejecutar solo migraciones
.\setup-complete.ps1 -OnlyMigrations
```

### **Error: Internal Server Error 500**
```powershell
# Verificar configuración y recrear admin
.\setup-complete.ps1 -OnlyAdmin
```

### **Scripts .bat no funcionan**
```powershell
# Los scripts .bat ahora llaman a PowerShell automáticamente
# También puedes usar directamente los .ps1
.\start-backend.ps1
```

### **Errores PostCSS/Babel**
```powershell
# Ya solucionados con postcss.config.cjs y vite.config.ts optimizado
# Si persisten errores:
cd frontend
Remove-Item -Recurse -Force node_modules
npm install
```

### **Problemas de permisos en Windows**
```powershell
# Ejecutar como Administrador
.\fix-windows-issues.ps1
```

---

## 📁 ESTRUCTURA DE ARCHIVOS CREADOS

```
📁 Cafeteria IA/
├── 🔧 setup-complete.ps1       # Script principal de configuración
├── 🔧 setup-complete.bat       # Wrapper .bat para el script PS
├── 🚀 start-backend.ps1        # Iniciar backend
├── 🚀 start-backend.bat        # Wrapper .bat para backend
├── 🎨 start-frontend.ps1       # Iniciar frontend  
├── 🎨 start-frontend.bat       # Wrapper .bat para frontend
├── 🌟 start-all.ps1            # Iniciar ambos servidores
├── 🌟 start-all.bat            # Wrapper .bat para ambos
├── 🛠️ fix-windows-issues.ps1   # Solucionar problemas Windows
├── 📖 SETUP-INSTRUCTIONS.md    # Este archivo
├── 📁 backend/
│   ├── 👤 create_admin.py      # Script crear administrador
│   ├── 🗃️ alembic.ini          # Configuración Alembic
│   ├── 🗃️ alembic/env.py       # Entorno migraciones
│   └── 🗃️ alembic/versions/    # Migraciones generadas
└── 📁 frontend/
    ├── ⚙️ postcss.config.cjs   # PostCSS (CommonJS)
    ├── 🎨 tailwind.config.js   # TailwindCSS
    └── ⚡ vite.config.ts       # Vite optimizado
```

---

## ✅ VERIFICACIÓN FINAL

Después de ejecutar `setup-complete.ps1`, deberías ver:

```
✅ Backend configurado (FastAPI + PostgreSQL)
✅ Migraciones ejecutadas  
✅ Usuario administrador creado
✅ Frontend configurado (React + Vite + TailwindCSS)

🔑 Username: admin
🔑 Password: TuPassword123

🌐 Frontend: http://localhost:5173
🌐 Backend:  http://localhost:8000
🌐 API Docs: http://localhost:8000/docs
```

---

## 🎉 ¡PROYECTO LISTO!

**Tu aplicación Cafeteria IA está completamente configurada y lista para desarrollo.**

Para cualquier problema, ejecuta `.\fix-windows-issues.ps1` o revisa los logs de los scripts.

---

*Generado automáticamente por el sistema de configuración de Cafeteria IA* 🤖