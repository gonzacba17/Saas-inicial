# Guía de Creación de Administrador - Desarrollo

## 🔒 Seguridad Primero

**ADVERTENCIA CRÍTICA:** Este script está diseñado EXCLUSIVAMENTE para ambientes de desarrollo local. Cuenta con múltiples validaciones de seguridad que impiden su ejecución en producción.

### ⚠️ Restricciones de Seguridad

El script se bloqueará automáticamente si detecta:
- Variables de entorno `ENVIRONMENT` o `ENV` configuradas como "production", "prod", o "prd"
- Hostname que contenga indicadores de producción (prod, aws, ec2, cloud, etc.)
- Database URL que apunte a servicios de producción (AWS RDS, Azure, GCP)
- Host de PostgreSQL que no sea localhost/127.0.0.1

---

## 📋 Requisitos Previos

### 1. Dependencias

```bash
# Instalar dependencias de desarrollo
pip install bcrypt==4.1.2
pip install email-validator==2.1.0
pip install python-dotenv==1.0.0
```

O instalar desde `requirements-dev.txt`:

```bash
pip install -r requirements-dev.txt
```

### 2. Base de Datos

Asegúrate de tener PostgreSQL o SQLite configurado y accesible:

```bash
# Verificar conexión a PostgreSQL
psql -U postgres -h localhost

# O verificar variables de entorno
echo $POSTGRES_HOST
echo $POSTGRES_USER
echo $POSTGRES_DB
```

---

## 🚀 Uso del Script

### Modo 1: Interactivo (Recomendado)

El modo más seguro y guiado paso a paso:

```bash
python scripts/create_dev_admin.py
```

El script te pedirá:
1. ✅ Confirmación de que estás en ambiente de desarrollo
2. 📧 Email del administrador (default: admin@dev.local)
3. 👤 Username (default: admin)
4. 🔐 Contraseña segura (con validación estricta)
5. 💾 Si deseas insertar directamente en la BD

### Modo 2: Con Email Predefinido

```bash
python scripts/create_dev_admin.py --email admin@dev.local
```

### Modo 3: Solo Generar SQL (Dry Run)

Genera el SQL sin ejecutar nada:

```bash
python scripts/create_dev_admin.py --dry-run --email admin@dev.local
```

El SQL se guardará en: `backend/logs/create_admin_YYYYMMDD_HHMMSS.sql`

### Modo 4: Inserción Directa

Inserta directamente sin preguntar:

```bash
python scripts/create_dev_admin.py --direct-insert --email admin@dev.local
```

---

## 🔐 Requisitos de Contraseña

Las contraseñas deben cumplir **TODOS** estos requisitos:

| Requisito | Descripción | Ejemplo |
|-----------|-------------|---------|
| **Longitud** | Mínimo 12 caracteres | ✅ `MyP@ssw0rd123` |
| **Mayúsculas** | Al menos 1 letra mayúscula | ✅ `P` en `MyP@ssw0rd` |
| **Minúsculas** | Al menos 1 letra minúscula | ✅ `y` en `MyP@ssw0rd` |
| **Números** | Al menos 1 dígito | ✅ `0`, `1`, `2`, `3` |
| **Símbolos** | Al menos 1 carácter especial | ✅ `@` en `MyP@ssw0rd` |
| **Sin palabras débiles** | No contener: password, admin, 123456, qwerty, saas, cafeteria | ❌ `Admin123!` |
| **Sin secuencias** | No contener: abc, 123, xyz, qwe, asd | ❌ `MyAbc123!` |

### ✅ Ejemplos de Contraseñas Válidas

```
MyV3ry$ecur3P@ss
C0mpl3x!P@ssw0rd
Str0ng&S3cur3#Key
Un1qu3$P@ssphrase!
```

### ❌ Ejemplos de Contraseñas Rechazadas

```
Admin123!          # Contiene "admin"
Password123!       # Contiene "password"
Short1!            # Menos de 12 caracteres
NoNumbers!@#       # Sin números
nouppercas3!       # Sin mayúsculas
NOLOWERCASE1!      # Sin minúsculas
NoSpecialChar1     # Sin símbolos especiales
MyPassAbc123!      # Contiene secuencia "abc"
```

---

## 📝 Proceso de Validación de Ambiente

El script ejecuta 6 validaciones de seguridad:

```
1. ✅ Variable ENVIRONMENT != production
2. ✅ Variable ENV != production  
3. ✅ Hostname no contiene indicadores de producción
4. ✅ DATABASE_URL no apunta a producción
5. ✅ POSTGRES_HOST es localhost/local
6. ✅ Confirmación explícita del usuario: "SI"
```

Si **CUALQUIERA** de estas validaciones falla, el script se detiene inmediatamente.

---

## 🔍 Ejemplos de Uso

### Ejemplo 1: Crear Admin con Email Personalizado

```bash
$ python scripts/create_dev_admin.py --email maria@dev.local

============================================================
🔧 SCRIPT DE CREACIÓN DE ADMINISTRADOR - DESARROLLO
============================================================

============================================================
⚠️  VERIFICACIÓN DE AMBIENTE
============================================================
Ambiente detectado: development
Hostname: dev-laptop
Database: localhost
============================================================

¿Confirmas que estás en tu máquina local de DESARROLLO? (escribe 'SI'): SI
✅ Validación de ambiente: OK

📧 Email: maria@dev.local
👤 Username (default: admin): maria_admin

🔐 Configuración de contraseña
Requisitos:
  - Mínimo 12 caracteres
  - Al menos 1 mayúscula, 1 minúscula, 1 número, 1 símbolo
  - No debe contener palabras comunes

Contraseña: ************
Confirmar contraseña: ************
✅ Contraseña cumple todos los requisitos

============================================================
📝 SQL GENERADO:
============================================================
...
💾 SQL guardado en: backend/logs/create_admin_20250105_143022.sql

¿Deseas insertar este usuario ahora en la BD? (SI/no): SI

🔄 Insertando usuario en la base de datos...
✨ Creando nuevo usuario: maria@dev.local

============================================================
✅ USUARIO ADMINISTRADOR CREADO EXITOSAMENTE
============================================================
📧 Email:     maria@dev.local
👤 Username:  maria_admin
🆔 User ID:   f47ac10b-58cc-4372-a567-0e02b2c3d479
🏷️  Role:      admin
🔐 Superuser: True
✅ Active:    True
============================================================

✅ Proceso completado exitosamente
```

### Ejemplo 2: Solo Generar SQL (Sin Insertar)

```bash
$ python scripts/create_dev_admin.py --dry-run --email test@dev.local

# Validaciones...

============================================================
📝 SQL GENERADO:
============================================================

-- Script SQL para crear administrador
-- Generado: 2025-01-05T14:35:12.123456
-- SOLO para ambientes de DESARROLLO

INSERT INTO users (id, email, username, hashed_password, role, is_active, is_superuser, created_at)
VALUES (
    '123e4567-e89b-12d3-a456-426614174000',
    'test@dev.local',
    'admin',
    '$2b$12$hashed_password_here...',
    'admin',
    true,
    true,
    NOW()
)
ON CONFLICT (email) DO UPDATE SET
    username = EXCLUDED.username,
    hashed_password = EXCLUDED.hashed_password,
    role = EXCLUDED.role,
    is_superuser = EXCLUDED.is_superuser,
    updated_at = NOW();

============================================================
💾 SQL guardado en: backend/logs/create_admin_20250105_143512.sql

✅ Proceso completado exitosamente
```

---

## 🛡️ Seguridad de Contraseñas

### Hashing con Bcrypt

El script utiliza **bcrypt** con un cost factor de **12** (recomendado para 2025):

```python
hashed_password = bcrypt.hashpw(
    password.encode('utf-8'),
    bcrypt.gensalt(rounds=12)  # Cost factor 12
).decode('utf-8')
```

### ¿Por qué Cost Factor 12?

- **Cost Factor 10** (antiguo estándar): ~100ms para generar hash
- **Cost Factor 12** (actual): ~400ms para generar hash
- Más lento = más seguro contra ataques de fuerza bruta
- Incremento exponencial: cada +1 duplica el tiempo

---

## 📊 Logging y Auditoría

Todos los eventos se registran en: `backend/logs/admin_creation.log`

Información registrada:
- ✅ Timestamp de ejecución
- ✅ Email y username (NO contraseñas)
- ✅ User ID generado
- ✅ Validaciones de ambiente
- ✅ Resultado de operación (éxito/error)

### Ejemplo de Log:

```
2025-01-05 14:30:15,123 - __main__ - INFO - ============================================================
2025-01-05 14:30:15,124 - __main__ - INFO - Iniciando generación de usuario administrador
2025-01-05 14:30:15,125 - __main__ - INFO - Timestamp: 2025-01-05T14:30:15.125000
2025-01-05 14:30:15,126 - __main__ - INFO - ============================================================
2025-01-05 14:30:20,456 - __main__ - INFO - Email validado: admin@dev.local
2025-01-05 14:30:20,457 - __main__ - INFO - Username: admin
2025-01-05 14:30:35,789 - __main__ - INFO - Generando hash de contraseña...
2025-01-05 14:30:36,200 - __main__ - INFO - ✅ Hash de contraseña generado exitosamente
2025-01-05 14:30:40,500 - __main__ - INFO - ✅ Usuario administrador creado exitosamente
2025-01-05 14:30:40,501 - __main__ - INFO - User ID: f47ac10b-58cc-4372-a567-0e02b2c3d479
2025-01-05 14:30:40,502 - __main__ - INFO - Email: admin@dev.local
2025-01-05 14:30:40,503 - __main__ - INFO - Role: admin
```

---

## 🧪 Tests Automatizados

Ejecutar tests del script:

```bash
# Todos los tests
python -m pytest backend/tests/test_create_admin.py -v

# Tests específicos
python -m pytest backend/tests/test_create_admin.py::TestEnvironmentValidation -v
python -m pytest backend/tests/test_create_admin.py::TestPasswordValidation -v
```

### Cobertura de Tests

- ✅ Validación de ambiente (8 tests)
- ✅ Validación de contraseñas (7 tests)
- ✅ Validación de emails (2 tests)
- ✅ Generación de SQL (1 test)
- ✅ Hashing bcrypt (2 tests)

**Total: 20 tests unitarios**

---

## ❌ Troubleshooting

### Error: "bcrypt no está instalado"

```bash
pip install bcrypt==4.1.2
```

### Error: "email-validator no está instalado"

```bash
pip install email-validator==2.1.0
```

### Error: "No se pudo conectar a la base de datos"

1. Verificar que PostgreSQL esté corriendo:
   ```bash
   sudo service postgresql status
   ```

2. Verificar variables de entorno:
   ```bash
   cat .env | grep POSTGRES
   ```

3. Usar modo `--dry-run` y ejecutar SQL manualmente:
   ```bash
   python scripts/create_dev_admin.py --dry-run
   psql -U postgres -d saas_cafeterias -f backend/logs/create_admin_*.sql
   ```

### Error: "BLOQUEADO: Este script no puede ejecutarse en producción"

✅ **Esto es correcto.** El script está funcionando como debe.

Si estás seguro de que estás en desarrollo:
1. Verifica variables de entorno: `env | grep -i prod`
2. Verifica hostname: `hostname`
3. Verifica database URL: `echo $DATABASE_URL`

---

## 🔄 Actualizar Contraseña de Admin Existente

Si el admin ya existe, el script preguntará si deseas sobrescribirlo:

```bash
$ python scripts/create_dev_admin.py --email admin@dev.local

# ...validaciones...

⚠️  Usuario 'admin@dev.local' ya existe en la base de datos
¿Deseas sobrescribir? (escribe 'SI'): SI

# Continúa con nueva contraseña...
```

---

## 📚 Referencias

- [Bcrypt Documentation](https://github.com/pyca/bcrypt/)
- [Email Validator](https://github.com/JoshData/python-email-validator)
- [OWASP Password Guidelines 2025](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

## 🤝 Soporte

Si encuentras problemas:

1. Revisa los logs: `backend/logs/admin_creation.log`
2. Ejecuta los tests: `pytest backend/tests/test_create_admin.py`
3. Verifica las variables de entorno
4. Usa modo `--dry-run` para debug

---

**Última actualización:** 2025-01-05  
**Versión del script:** 1.0.0
