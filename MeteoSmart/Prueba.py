import requests
import cx_Oracle
import json
from datetime import datetime, timezone


# Configuración de la conexión Oracle
conn = cx_Oracle.connect("system", "pythonoracle", "localhost/XE")
cursor = conn.cursor()

# Parámetros de la API
API_KEY = '0c68f74e08071a11ea5cfaddf4f26bb7'
ciudad = 'Madrid'
url = f'https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={API_KEY}&units=metric&lang=es'

# 1. Llamar a la API
response = requests.get(url)
data = response.json()

# 2. Extraer datos clave
nombre_ciudad = data['name']
pais = data['sys']['country']
lat = data['coord']['lat']
lon = data['coord']['lon']
temp = data['main']['temp']
humedad = data['main']['humidity']
viento = data['wind']['speed']
fecha_hora = datetime.fromtimestamp(data['dt'], tz=timezone.utc)
condicion_id = data['weather'][0]['id']
descripcion = data['weather'][0]['description']
icono = data['weather'][0]['icon']
json_str = json.dumps(data)

# 3. Insertar ciudad si no existe
cursor.execute("SELECT COUNT(*) FROM Ciudad WHERE nombre = :1 AND país = :2", (nombre_ciudad, pais))
if cursor.fetchone()[0] == 0:
    # Esto ya no chocará con IDs existentes
    cursor.execute("""
        INSERT INTO Ciudad (idCiudad, nombre, país, lat, lon)
        VALUES (SEQ_CIUDAD.NEXTVAL, :1, :2, :3, :4)
    """, (nombre_ciudad, pais, lat, lon))
    conn.commit()

# Obtener idCiudad
cursor.execute("SELECT idCiudad FROM Ciudad WHERE nombre = :1 AND país = :2", (nombre_ciudad, pais))
id_ciudad = cursor.fetchone()[0]

# 4. Insertar condición si no existe
cursor.execute("SELECT COUNT(*) FROM Condicion WHERE idCondicion = :1", (condicion_id,))
if cursor.fetchone()[0] == 0:
    cursor.execute("""
        INSERT INTO Condicion (idCondicion, descripcion, icono)
        VALUES (:1, :2, :3)
    """, (condicion_id, descripcion, icono))
    conn.commit()

# 5. Insertar clima (usa tu procedimiento)
cursor.callproc("insertar_clima", [id_ciudad, temp, humedad, viento, fecha_hora])

# 6. Obtener último idRegistro insertado (por ejemplo con MAX)
cursor.execute("SELECT MAX(idRegistro) FROM RegistroClima WHERE idCiudad = :1", (id_ciudad,))
id_registro = cursor.fetchone()[0]

# 7. Insertar ClimaCondicion
cursor.execute("""
    INSERT INTO ClimaCondicion (id, idRegistro, idCondicion)
    VALUES (SEQ_CLIMACONDICION.NEXTVAL, :1, :2)
""", (id_registro, condicion_id))

# 8. Insertar ApiLog
cursor.execute("""
    INSERT INTO ApiLog (idLog, endpoint, respuesta_json, fecha_hora)
    VALUES (SEQ_APILOG.NEXTVAL, :1, :2, SYSTIMESTAMP)
""", (url, json_str))

conn.commit()
cursor.close()
conn.close()
