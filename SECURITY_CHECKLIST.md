# ✅ Checklist de Seguridad para GitHub

## 🔒 Verificaciones Realizadas

### ✅ Archivos Sensibles
- [x] `.env` está en `.gitignore` (no se subirá)
- [x] `db.sqlite3` está en `.gitignore` (no se subirá)
- [x] `venv/` y `.venv/` están en `.gitignore` (no se subirán)
- [x] `logs/` está en `.gitignore` (no se subirá)
- [x] `.idea/` está en `.gitignore` (no se subirá)

### ✅ Configuración de Seguridad
- [x] `SECRET_KEY` no está hardcodeado (usa variables de entorno)
- [x] `DEBUG` usa variables de entorno (por defecto True solo en desarrollo)
- [x] Configuración de seguridad para producción incluida
- [x] `.env.example` creado como plantilla (sí se puede subir)

### ✅ Archivos Eliminados
- [x] Scripts temporales eliminados (`setup_env.ps1`, `setup_env.bat`, etc.)
- [x] Scripts de limpieza eliminados

### ✅ Archivos que SÍ se suben a GitHub
- ✅ `README.md` - Documentación del proyecto
- ✅ `requirements.txt` - Dependencias del proyecto
- ✅ `.env.example` - Plantilla de variables de entorno
- ✅ Código fuente (`.py`, `.html`, `.css`)
- ✅ `.gitignore` - Configuración de Git

### ❌ Archivos que NO se suben a GitHub
- ❌ `.env` - Variables de entorno con credenciales
- ❌ `db.sqlite3` - Base de datos local
- ❌ `venv/` - Entorno virtual
- ❌ `logs/` - Archivos de log
- ❌ `.idea/` - Configuración del IDE
- ❌ `__pycache__/` - Archivos compilados de Python

## 🚀 Antes de Subir a GitHub

### 1. Verifica que no hay archivos sensibles
```bash
# Verifica que .env no está en el staging
git status

# Si aparece .env, no lo agregues:
git reset .env
```

### 2. Crea el archivo .env localmente
```bash
cd MeteoSmart/clima
cp .env.example .env
# Edita .env con tus credenciales reales
```

### 3. Verifica el .gitignore
```bash
# Asegúrate de que estos archivos NO aparecen en git status:
git status
# No deberías ver: .env, db.sqlite3, venv/, logs/
```

## 📝 Comandos Git Recomendados

```bash
# 1. Verificar qué se va a subir
git status

# 2. Agregar archivos (NO agregues .env, db.sqlite3, venv/)
git add .

# 3. Verificar nuevamente
git status

# 4. Commit
git commit -m "Initial commit: MeteoSmart project"

# 5. Push
git push origin main
```

## ⚠️ IMPORTANTE

- **NUNCA** subas el archivo `.env` con credenciales reales
- **NUNCA** subas `db.sqlite3` con datos de usuarios
- **SIEMPRE** verifica `git status` antes de hacer commit
- El archivo `.env.example` es seguro de subir (solo plantilla)

## 🔐 Si accidentalmente subiste credenciales

1. **Revoca inmediatamente** las credenciales expuestas:
   - API Key de OpenWeatherMap: genera una nueva
   - Oracle credentials: cambia las contraseñas
   - Django SECRET_KEY: genera uno nuevo

2. **Elimina del historial de Git** (si es necesario):
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
   ```

3. **Fuerza el push** (solo si es necesario y tienes permiso):
   ```bash
   git push origin --force --all
   ```

