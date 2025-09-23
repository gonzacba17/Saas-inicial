# 🤝 Guía de Contribución - SaaS Cafeterías

¡Gracias por tu interés en contribuir al proyecto SaaS Cafeterías! Esta guía te ayudará a configurar tu entorno de desarrollo y seguir las mejores prácticas del proyecto.

## 📋 Índice

- [🚀 Setup de Desarrollo](#-setup-de-desarrollo)
- [📂 Estructura del Proyecto](#-estructura-del-proyecto)
- [💻 Estilo de Código](#-estilo-de-código)
- [🧪 Testing](#-testing)
- [📝 Commits y PRs](#-commits-y-prs)
- [🔧 Scripts de Desarrollo](#-scripts-de-desarrollo)

## 🚀 Setup de Desarrollo

### Prerrequisitos
- Python 3.11+
- Node.js 20+
- Git
- PostgreSQL (opcional, se puede usar SQLite para desarrollo)

### Configuración Inicial

**Opción 1: Setup Automatizado (Recomendado)**
```bash
# Clonar el repositorio
git clone https://github.com/gonzacba17/Saas-inicial.git
cd Saas-inicial

# Setup automático
./scripts/update_and_test.sh        # Linux/Mac
.\scripts\update_and_test.ps1       # Windows
```

**Opción 2: Setup Manual**
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac o venv\Scripts\activate en Windows
pip install -r requirements.txt
python create_admin.py

# Frontend (en otra terminal)
cd frontend
npm install

# Validar setup
python tests/full_test.py
```

## 📂 Estructura del Proyecto

```
Saas-inicial/
├── backend/                # API FastAPI
│   ├── app/
│   │   ├── api/v1/        # Endpoints REST organizados por dominio
│   │   ├── core/          # Configuración central
│   │   ├── db/            # Modelos SQLAlchemy y CRUD
│   │   ├── middleware/    # Middleware de seguridad/validación
│   │   └── services_directory/  # Servicios especializados
│   └── alembic/           # Migraciones de BD
├── frontend/              # SPA React TypeScript
├── tests/                 # Testing completo
├── scripts/               # Scripts de automatización
├── docs/                  # Documentación
└── monitoring/            # Observabilidad
```

### Convenciones de Directorios

- **Backend**: Sigue patrón de separación por capas (API → Services → DB)
- **Frontend**: Organización por funcionalidad (pages, components, store)
- **Tests**: Un archivo por módulo principal + suite de integración
- **Scripts**: Automatización de desarrollo, testing y deployment

## 💻 Estilo de Código

### Python (Backend)
```bash
# Linting y formateo
cd backend
ruff check . --fix
black .
isort .
```

**Convenciones:**
- Usar type hints en todas las funciones
- Docstrings para clases y funciones públicas
- Seguir PEP 8
- Nombres descriptivos para variables y funciones

**Ejemplo:**
```python
from typing import List, Optional
from sqlalchemy.orm import Session

def get_user_businesses(
    db: Session, 
    user_id: str, 
    skip: int = 0, 
    limit: int = 100
) -> List[Business]:
    """
    Obtiene los negocios asociados a un usuario.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        skip: Número de registros a saltar
        limit: Límite de registros a retornar
        
    Returns:
        Lista de negocios del usuario
    """
    return db.query(Business).filter(
        Business.owner_id == user_id
    ).offset(skip).limit(limit).all()
```

### TypeScript (Frontend)
```bash
# Linting y formateo
cd frontend
npm run lint
npm run format
```

**Convenciones:**
- Usar TypeScript estricto
- Componentes funcionales con hooks
- Tipado explícito para props e interfaces
- Nombres de componentes en PascalCase

**Ejemplo:**
```typescript
interface BusinessCardProps {
  business: Business;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

export const BusinessCard: React.FC<BusinessCardProps> = ({
  business,
  onEdit,
  onDelete
}) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold">{business.name}</h3>
      <p className="text-gray-600">{business.description}</p>
    </div>
  );
};
```

## 🧪 Testing

### Ejecutar Tests
```bash
# Suite completa de tests
python tests/full_test.py

# Tests específicos del backend
cd backend
pytest tests/test_auth.py -v

# Tests específicos del frontend
cd frontend
npm test
```

### Escribir Tests

**Backend (pytest):**
```python
def test_create_user_success(db_session):
    """Test que verifica la creación exitosa de usuario."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePass123!"
    }
    
    user = create_user(db_session, UserCreate(**user_data))
    
    assert user.email == user_data["email"]
    assert user.username == user_data["username"]
    assert user.is_active is True
```

**Frontend (Vitest + RTL):**
```typescript
import { render, screen } from '@testing-library/react';
import { LoginForm } from './LoginForm';

test('renders login form correctly', () => {
  render(<LoginForm />);
  
  expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
});
```

### Criterios de Calidad
- **Coverage**: Mínimo 70% en nuevas funcionalidades
- **Tests unitarios**: Para lógica de negocio crítica
- **Tests de integración**: Para flujos completos
- **Tests E2E**: Para funcionalidades principales

## 📝 Commits y PRs

### Formato de Commits
Usar [Conventional Commits](https://www.conventionalcommits.org/):

```bash
tipo(scope): descripción breve

[cuerpo opcional]

[footer opcional]
```

**Tipos:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Cambios de formato (sin afectar lógica)
- `refactor`: Refactoring de código
- `test`: Agregar o modificar tests
- `chore`: Tareas de mantenimiento

**Ejemplos:**
```bash
feat(auth): agregar sistema de roles para usuarios
fix(api): corregir validación de email en registro
docs(readme): actualizar instrucciones de instalación
test(auth): agregar tests para login con roles
```

### Pull Requests

**Antes de crear un PR:**
1. Ejecutar tests: `python tests/full_test.py`
2. Verificar linting: `ruff check backend/` y `npm run lint` en frontend
3. Actualizar documentación si es necesario
4. Probar manualmente la funcionalidad

**Template de PR:**
```markdown
## 📝 Descripción
Breve descripción de los cambios realizados.

## 🔧 Tipo de cambio
- [ ] Bug fix
- [ ] Nueva funcionalidad
- [ ] Breaking change
- [ ] Documentación

## 🧪 Testing
- [ ] Tests unitarios pasan
- [ ] Tests de integración pasan
- [ ] Funcionalidad probada manualmente

## 📋 Checklist
- [ ] Código sigue el estilo del proyecto
- [ ] Self-review del código realizado
- [ ] Documentación actualizada
- [ ] Tests agregados/actualizados
```

## 🔧 Scripts de Desarrollo

### Scripts Principales
```bash
# Setup completo + testing
./scripts/update_and_test.sh

# Solo testing
python tests/full_test.py

# Deployment
./scripts/deploy.sh production
```

### Desarrollo Diario
```bash
# Iniciar desarrollo backend
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload

# Iniciar desarrollo frontend (otra terminal)
cd frontend
npm run dev

# Ejecutar tests antes de commit
python tests/full_test.py
```

### Comandos Útiles
```bash
# Crear nueva migración
cd backend && alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
cd backend && alembic upgrade head

# Resetear usuario admin
cd backend && python create_admin.py

# Verificar estado de la aplicación
curl http://localhost:8000/health
```

## 🐛 Debugging

### Logs y Debugging
- **Backend**: Logs en consola con nivel configurado en `.env`
- **Frontend**: Chrome DevTools y React Developer Tools
- **Base de datos**: Logs de queries en development

### Herramientas Recomendadas
- **VSCode** con extensiones Python y TypeScript
- **Postman** para testing de API (ver `cafeteria_ia_postman_collection.json`)
- **pgAdmin** para gestión de PostgreSQL

## 🆘 Ayuda y Soporte

### Recursos
- **Documentación API**: http://localhost:8000/docs
- **Arquitectura**: [docs/](docs/) para documentación detallada
- **Issues**: Reportar bugs en GitHub Issues

### Contacto
- **Preguntas técnicas**: Crear issue en GitHub
- **Propuestas de mejora**: Usar GitHub Discussions

---

¡Gracias por contribuir al proyecto! 🚀

Recuerda seguir estas guías para mantener la calidad y consistencia del código.