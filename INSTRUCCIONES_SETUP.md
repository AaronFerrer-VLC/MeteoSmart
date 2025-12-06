# Instrucciones para Configurar el Entorno

## 🚀 Configuración Rápida

### Opción 1: Script Automático (Recomendado)

**Windows (PowerShell):**
```powershell
cd C:\Users\aaron\MeteoSmart\MeteoSmart
.\setup_env.ps1
```

**Windows (CMD):**
```cmd
cd C:\Users\aaron\MeteoSmart\MeteoSmart
setup_env.bat
```

### Opción 2: Manual

1. **Navegar al directorio del proyecto:**
   ```powershell
   cd C:\Users\aaron\MeteoSmart\MeteoSmart\clima
   ```

2. **Crear entorno virtual:**
   ```powershell
   python -m venv venv
   ```

3. **Activar entorno virtual:**
   ```powershell
   # PowerShell
   .\venv\Scripts\Activate.ps1
   
   # CMD
   venv\Scripts\activate.bat
   ```

   ⚠️ **Si PowerShell da error de ejecución:**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **Actualizar pip:**
   ```powershell
   python -m pip install --upgrade pip
   ```

5. **Instalar dependencias:**
   ```powershell
   pip install -r requirements.txt
   ```

## ✅ Verificar Instalación

Después de instalar, verifica que Django esté instalado:

```powershell
python manage.py --version
```

Deberías ver: `5.2.3` (o la versión instalada)

## 🏃 Ejecutar el Proyecto

1. **Asegúrate de estar en el directorio correcto:**
   ```powershell
   cd C:\Users\aaron\MeteoSmart\MeteoSmart\clima
   ```

2. **Activa el entorno virtual:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. **Ejecuta el servidor:**
   ```powershell
   python manage.py runserver
   ```

4. **Abre tu navegador en:**
   ```
   http://127.0.0.1:8000/
   ```

## 📝 Notas Importantes

- **Siempre activa el entorno virtual** antes de ejecutar comandos de Django
- El entorno virtual se crea en `MeteoSmart/clima/venv/`
- Este directorio está en `.gitignore`, no se subirá al repositorio
- Si cambias de terminal, necesitas reactivar el entorno virtual

## 🔧 Solución de Problemas

### Error: "No module named 'django'"
- Asegúrate de haber activado el entorno virtual
- Verifica que las dependencias se instalaron: `pip list`

### Error de ejecución de scripts en PowerShell
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error al instalar cx-Oracle
- Puede requerir Oracle Instant Client
- Para desarrollo, puedes comentar temporalmente `cx-Oracle` en `requirements.txt`

