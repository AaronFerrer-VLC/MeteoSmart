# MeteoSmart 🌤️

MeteoSmart es una aplicación Django moderna y profesional que integra datos meteorológicos de OpenWeatherMap y gestiona usuarios con extensión en una base de datos Oracle. El proyecto incluye autenticación, gestión de preferencias de usuario y consulta de información climática en tiempo real con una interfaz moderna y responsive.

---

## 🚀 Características

✅ **Autenticación de usuarios** - Registro e inicio de sesión seguro  
✅ **Almacenamiento extendido** - Información del usuario sincronizada con Oracle  
✅ **Consulta meteorológica** - Datos en tiempo real de OpenWeatherMap  
✅ **Pronósticos detallados** - Por horas y por días con información completa  
✅ **Ciudades favoritas** - Guarda tus ciudades preferidas  
✅ **Historial de consultas** - Revisa tus búsquedas anteriores  
✅ **Interfaz moderna** - Diseño responsive con gradientes y animaciones  
✅ **Logging estructurado** - Sistema de logs para debugging y monitoreo  
✅ **Código profesional** - Arquitectura limpia, documentada y mantenible

---

## ⚙️ Tecnologías utilizadas

- **Python 3.x**
- **Django 5.2.3** - Framework web
- **Oracle Database** (vía `cx_Oracle`) - Base de datos empresarial
- **OpenWeatherMap API** - Datos meteorológicos
- **Bootstrap 5.3.3** - Framework CSS
- **Font Awesome 6.5.1** - Iconos modernos
- **python-dotenv** - Gestión de variables de entorno
- **HTML5 / CSS3** - Interfaz moderna con gradientes y animaciones

---

## 🏗️ Estructura del proyecto

```
MeteoSmart/
├── clima/                      # Proyecto Django
│   ├── clima/                  # Configuración principal
│   │   ├── settings.py         # Configuración mejorada con variables de entorno
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── Meteo/                  # Aplicación principal
│   │   ├── migrations/
│   │   ├── templates/          # Templates HTML modernizados
│   │   ├── static/css/         # CSS moderno con gradientes
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py           # Modelos con documentación completa
│   │   ├── signals.py          # Signals mejorados
│   │   ├── urls.py             # URLs organizadas
│   │   ├── utils.py            # Utilidades y helpers
│   │   └── views.py            # Views refactorizadas y documentadas
│   ├── logs/                   # Directorio de logs
│   ├── static/css/
│   │   └── style.css           # CSS moderno y responsive
│   ├── .env.example            # Ejemplo de variables de entorno
│   ├── .gitignore              # Archivos ignorados por Git
│   ├── requirements.txt        # Dependencias del proyecto
│   ├── db.sqlite3              # Base de datos SQLite (desarrollo)
│   └── manage.py
└── README.md
```

---

## 🔐 Configuración de variables de entorno

Copia el archivo `.env.example` a `.env` y configura las siguientes variables:

```env
# Django Settings
DJANGO_SECRET_KEY=tu-secret-key-seguro-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_LOG_LEVEL=INFO

# OpenWeatherMap API
OPENWEATHERMAP_API_KEY=tu-api-key-de-openweathermap

# Oracle Database
ORACLE_USER=tu-usuario-oracle
ORACLE_PASSWORD=tu-password-oracle
ORACLE_DSN=localhost/XE
```

**⚠️ IMPORTANTE:** Nunca subas el archivo `.env` al repositorio. Está incluido en `.gitignore`.

---

## 🛠️ Instalación y ejecución

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/AaronFerrer-VLC/MeteoSmart.git
cd MeteoSmart/MeteoSmart/clima
```

### 2️⃣ Crear y activar entorno virtual

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar variables de entorno

Copia `.env.example` a `.env` y completa con tus credenciales:

```bash
# Windows
copy .env.example .env

# Linux/macOS
cp .env.example .env
```

Edita `.env` con tus valores reales.

### 5️⃣ Ejecutar migraciones

```bash
python manage.py migrate
```

### 6️⃣ Crear superusuario (opcional)

```bash
python manage.py createsuperuser
```

### 7️⃣ Iniciar el servidor de desarrollo

```bash
python manage.py runserver
```

Abre tu navegador en `http://127.0.0.1:8000/`

---

## 📋 Mejoras implementadas

### ✨ Calidad de código

- ✅ **Settings mejorado**: Separación de configuraciones dev/prod, uso de variables de entorno
- ✅ **Código refactorizado**: Eliminación de duplicación, funciones helper, context managers
- ✅ **Manejo de errores**: Try-catch mejorados, logging estructurado
- ✅ **Documentación**: Docstrings completos en todas las funciones y clases
- ✅ **Validaciones**: Validación de datos de entrada
- ✅ **Seguridad**: Configuraciones de seguridad para producción
- ✅ **Logging**: Sistema de logs configurado y estructurado

### 🎨 Interfaz moderna

- ✅ **Diseño moderno**: Gradientes, sombras, animaciones suaves
- ✅ **Responsive**: Diseño adaptativo para móviles, tablets y desktop
- ✅ **Iconos Font Awesome**: Iconos modernos en toda la aplicación
- ✅ **Animaciones**: Transiciones y efectos visuales mejorados
- ✅ **UX mejorada**: Mejor organización visual y feedback al usuario
- ✅ **Accesibilidad**: Mejoras en estructura HTML y navegación

### 🏗️ Arquitectura

- ✅ **Utils module**: Funciones helper reutilizables
- ✅ **Context managers**: Manejo seguro de conexiones a base de datos
- ✅ **URLs organizadas**: Estructura clara y sin duplicados
- ✅ **Models mejorados**: Documentación y validaciones
- ✅ **Forms mejorados**: Mejor UX en formularios

---

## 📝 Notas importantes

- ⚠️ **Nunca subas tu `.env`** - Está incluido en `.gitignore`
- ⚠️ **Si cometes tus claves, revócalas inmediatamente**
- ⚠️ **Para producción**, revisa:
  - Configuración de seguridad en `settings.py`
  - `DEBUG = False`
  - `ALLOWED_HOSTS` configurado correctamente
  - Variables de entorno seguras
  - Base de datos de producción

---

## 🧪 Testing

Para ejecutar los tests (cuando estén implementados):

```bash
python manage.py test
```

---

## 📊 Logs

Los logs se guardan en:

- Consola (durante desarrollo)
- `logs/django.log` (archivo de log)

Configura el nivel de logging en `.env` con `DJANGO_LOG_LEVEL`.

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está licenciado bajo MIT License.

---

## 👥 Autores

**Christian & Aarón** - España

---

## 🙏 Agradecimientos

- [OpenWeatherMap](https://openweathermap.org/) por la API de datos meteorológicos
- [Django](https://www.djangoproject.com/) por el framework web
- [Bootstrap](https://getbootstrap.com/) por el framework CSS
- [Font Awesome](https://fontawesome.com/) por los iconos

---

## 📞 Contacto

Para preguntas o sugerencias, abre un issue en el repositorio.

---

**⭐ Si te gusta este proyecto, dale una estrella! ⭐**
