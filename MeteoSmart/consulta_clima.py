import requests
import cx_Oracle
from datetime import datetime, timezone
import traceback

# --- CONFIGURACIÓN ---
API_KEY = '0c68f74e08071a11ea5cfaddf4f26bb7'  # Tu API key de OpenWeatherMap
DB_USER = 'system'
DB_PASSWORD = 'pythonoracle'  # ⚠️ Sustituye por la real
DB_DSN = 'localhost/XE'  # Cambia si usas otro servicio o nombre

# --- CONEXIÓN A ORACLE ---
try:
    connection = cx_Oracle.connect(DB_USER, DB_PASSWORD, DB_DSN)
    cursor = connection.cursor()
    print("✅ Conectado a Oracle correctamente.")
except Exception as err:
    print("❌ Error al conectar con Oracle:")
    traceback.print_exc()
    exit()

# --- INPUT CIUDAD ---
ciudad = input("\n🌍 Introduce el nombre de una ciudad: ").strip()

try:
    # --- LLAMADA A LA API ---
    url = f'https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={API_KEY}&units=metric&lang=es'
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        raise Exception(f"Error en API: {data.get('message', 'Sin mensaje')}")

    print("✅ Datos obtenidos de OpenWeatherMap.")

    # --- DATOS DE LA API ---
    nombre_ciudad = data['name']
    pais = data['sys']['country']
    lat = data['coord']['lat']
    lon = data['coord']['lon']
    temp = data['main']['temp']
    humedad = data['main']['humidity']
    viento = data['wind']['speed']
    fecha_hora = datetime.fromtimestamp(data['dt'], tz=timezone.utc)

    weather = data['weather'][0]
    id_cond = weather['id']
    desc = weather['description']
    icono = weather['icon']

    # --- INSERTAR O VERIFICAR CIUDAD ---
    cursor.execute("SELECT idCiudad FROM Ciudad WHERE nombre = :1 AND país = :2", (nombre_ciudad, pais))
    row = cursor.fetchone()

    if row:
        id_ciudad = row[0]
        print(f"ℹ️ Ciudad encontrada en BD (id {id_ciudad})")
    else:
        cursor.execute("SELECT NVL(MAX(idCiudad), 0) + 1 FROM Ciudad")
        id_ciudad = cursor.fetchone()[0]
        cursor.execute("""
            INSERT INTO Ciudad (idCiudad, nombre, país, lat, lon)
            VALUES (:1, :2, :3, :4, :5)
        """, (id_ciudad, nombre_ciudad, pais, lat, lon))
        print(f"➕ Ciudad insertada en BD (id {id_ciudad})")

    # --- LLAMADA AL PROCEDIMIENTO insertar_clima ---
    try:
        cursor.callproc("insertar_clima", [id_ciudad, temp, humedad, viento, fecha_hora])
        print("✅ RegistroClima insertado.")
    except Exception as e:
        print("⚠️ Fallo al insertar clima (posible duplicado):", e)

    # --- INSERTAR CONDICIÓN SI NO EXISTE ---
    cursor.execute("SELECT COUNT(*) FROM Condicion WHERE idCondicion = :1", (id_cond,))
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO Condicion (idCondicion, descripcion, icono)
            VALUES (:1, :2, :3)
        """, (id_cond, desc, icono))
        print(f"➕ Condición insertada ({desc})")
    else:
        print(f"ℹ️ Condición ya registrada ({desc})")

    # --- VINCULAR EN ClimaCondicion ---
    cursor.execute("""
        SELECT MAX(idRegistro)
        FROM RegistroClima
        WHERE idCiudad = :1
    """, (id_ciudad,))
    id_registro = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO ClimaCondicion (id, idRegistro, idCondicion)
        VALUES (SEQ_CLIMACONDICION.NEXTVAL, :1, :2)
    """, (id_registro, id_cond))
    print("🔗 Relación ClimaCondicion insertada.")

    # --- REGISTRAR EN ApiLog ---
    cursor.execute("""
        INSERT INTO ApiLog (idLog, endpoint, respuesta_json, fecha_hora)
        VALUES (SEQ_APILOG.NEXTVAL, :1, TO_CLOB(:2), SYSTIMESTAMP)
    """, (url, response.text))
    print("🗂️ Llamada registrada en ApiLog.")

    # --- COMMIT ---
    connection.commit()
    print("\n✅ Todos los datos se han guardado correctamente.\n")

    cursor.execute("""
            SELECT ROUND(AVG(temp), 2)
            FROM RegistroClima
            WHERE idCiudad = :1
              AND fecha_hora >= ADD_MONTHS(SYSDATE, -1)
        """, (id_ciudad,))
    temp_media = cursor.fetchone()[0]

    # --- RESUMEN EN PANTALLA ---
    print(f"📍 Ciudad: {nombre_ciudad} ({pais})")
    print(f"🌡️ Temperatura: {temp}°C")
    print(f"💧 Humedad: {humedad}%")
    print(f"🌬️ Viento: {viento} m/s")
    print(f"🌥️ Condición: {desc} ({icono})")
    print(f"🕒 Fecha/Hora (UTC): {fecha_hora}")
    print(f"🌡️ La temperatura media: {temp_media}")

except Exception as err:
    print("❌ Error durante la ejecución:")
    traceback.print_exc()

finally:
    cursor.close()
    connection.close()
    print("\n🔚 Conexión cerrada.")


