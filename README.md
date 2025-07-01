# MeteoSmart

MeteoSmart es una aplicación Django que integra datos meteorológicos de OpenWeatherMap y gestiona usuarios con extensión en una base de datos Oracle. El proyecto incluye autenticación, gestión de preferencias de usuario y consulta de información climática en tiempo real.

---

## 🚀 Características

✅ Registro e inicio de sesión de usuarios  
✅ Almacenamiento extendido de información del usuario en Oracle  
✅ Consulta de datos meteorológicos mediante la API de OpenWeatherMap  
✅ Gestión de preferencias (ciudad favorita)  
✅ Interfaz web sencilla desarrollada con Django  

---

## ⚙️ Tecnologías utilizadas

- **Python**
- **Django**
- **Oracle Database** (vía `cx_Oracle`)
- **OpenWeatherMap API**
- **HTML / CSS**
- **python-dotenv** para gestión de variables de entorno

---

## 🏗️ Estructura del proyecto

"# MeteoSmart" 

MeteoSmart/
├── .idea/                 # Configuración de PyCharm
├── .venv/                 # Entorno virtual
├── clima/                 # Proyecto Django
│   ├── clima/             # Configuración principal (settings, urls, wsgi)
│   └── Meteo/             # Aplicación Django
│       ├── migrations/
│       ├── templates/
│       ├── admin.py
│       ├── apps.py
│       ├── forms.py
│       ├── models.py
│       ├── signals.py
│       ├── tests.py
│       ├── urls.py
│       └── views.py
├── static/
│   └── css/
│       └── style.css
├── .env                   # Variables de entorno
├── .gitignore             # Ignora ficheros sensibles
├── db.sqlite3             # Base de datos SQLite
├── manage.py              # Comando principal de Django
└── README.md


## 🔐 Configuración de variables de entorno

Crea un archivo `.env` en la raíz del proyecto y añade:

OPENWEATHERMAP_API_KEY=tu_api_key
ORACLE_USER=tu_usuario_oracle
ORACLE_PASSWORD=tu_password_oracle
ORACLE_DSN=localhost/XE

Asegúrate de **NO subir este archivo al repositorio**.

---

## 🛠️ Instalación y ejecución

1️⃣ **Clonar el repositorio**

git clone https://github.com/AaronFerrer-VLC/MeteoSmart.git
cd MeteoSmart

2️⃣ **Crear y activar entorno virtual**

python -m venv .venv

source .venv/bin/activate  # Linux/macOS

.venv\Scripts\activate     # Windows

3️⃣ **Instalar dependencias**

pip install -r requirements.txt

4️⃣ **Configurar variables de entorno**

Crear .env como se muestra arriba.

5️⃣ **Ejecutar migraciones**

python manage.py migrate

6️⃣ **Crear superusuario (opcional)**

python manage.py createsuperuser

7️⃣ **Iniciar el servidor de desarrollo**

python manage.py runserver


## 📝 Notas importantes

Nunca subas tu .env. Está incluido en .gitignore.

Si cometes tus claves, revócalas inmediatamente.

Para producción, revisa configuración de seguridad y bases de datos.


## 🤝 Contribuciones
¡Las contribuciones son bienvenidas! Abre un issue o un pull request.

## 📄 Licencia
Este proyecto está licenciado bajo MIT License.

## 🌐 Autor

Christian & Aarón
