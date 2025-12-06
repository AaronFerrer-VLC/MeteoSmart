# 🔐 Configuración del archivo .env

## 📝 Pasos para configurar

### 1. Abre el archivo `.env`

El archivo `.env` está en: `MeteoSmart/clima/.env`

### 2. Configura la API Key de OpenWeatherMap

1. **Regístrate en OpenWeatherMap** (si no tienes cuenta):
   - Ve a: https://openweathermap.org/api
   - Crea una cuenta gratuita
   - Ve a "API keys" en tu perfil

2. **Copia tu API Key** y reemplaza en `.env`:
   ```env
   OPENWEATHERMAP_API_KEY=tu-api-key-aqui
   ```

### 3. Configura Oracle Database (si usas Oracle)

Si usas Oracle Database, configura:
```env
ORACLE_USER=tu-usuario
ORACLE_PASSWORD=tu-password
ORACLE_DSN=localhost/XE
```

Si **NO usas Oracle** (solo SQLite para desarrollo), puedes dejar estos valores o comentarlos.

### 4. Verifica la configuración

Después de configurar, reinicia el servidor Django:

```powershell
# Detén el servidor (Ctrl+C) y reinicia
python manage.py runserver
```

## ⚠️ Importante

- **NUNCA subas el archivo `.env` al repositorio Git**
- El archivo `.env` ya está en `.gitignore`
- El archivo `.env.example` es solo una plantilla (sí se sube a Git)

## 🔑 Obtener API Key de OpenWeatherMap

1. Ve a: https://openweathermap.org/api
2. Haz clic en "Sign Up" (es gratis)
3. Confirma tu email
4. Ve a "API keys" en tu perfil
5. Copia la "API key" (o crea una nueva)
6. Pégala en el archivo `.env`

## ✅ Verificación

Para verificar que la API key funciona, busca una ciudad en la aplicación. Si funciona, verás el clima. Si no, verás un error.

