import requests
import os
import cx_Oracle
from collections import defaultdict
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib import messages
from .forms import RegistroUsuarioForm
from django.contrib.admin.views.decorators import staff_member_required
from .models import UsuarioExtendido
from django.core.mail import send_mail
from django.conf import settings
from dotenv import load_dotenv

API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

def get_connection():
    user = os.getenv("ORACLE_USER")
    password = os.getenv("ORACLE_PASSWORD")
    dsn = os.getenv("ORACLE_DSN")
    return cx_Oracle.connect(user, password, dsn)


@login_required
def historial(request):
    conn = get_connection()
    cursor = conn.cursor()

    user_id = request.user.usuarioextendido.idusuario
    print(f">>> Historial: IDUSUARIO en Oracle = {user_id}")

    try:
        # Consulta historial
        cursor.execute("""
            SELECT c.nombre, c.pais, TO_CHAR(con.fecha_hora, 'DD/MM/YYYY HH24:MI:SS')
            FROM Consulta con
            JOIN Ciudad c ON c.idCiudad = con.idCiudad
            WHERE con.idUsuario = :1
            ORDER BY con.fecha_hora DESC
        """, [user_id])

        registros = cursor.fetchall()
        print(f">>> Registros encontrados: {registros}")

    except Exception as e:
        registros = []
        messages.error(request, f"Error al obtener el historial: {e}")
        print(">>> Error en consulta historial:", e)

    finally:
        cursor.close()
        conn.close()

    return render(request, "usuario/historial.html", {
        "registros": registros
    })


def clima_api(request):
    ciudad = request.GET.get('ciudad')
    datos = {}
    error = None
    pronostico = []
    pronostico_diario = []

    if ciudad:
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # --- Clima actual ---
            url = f'https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={API_KEY}&units=metric&lang=es'
            response = requests.get(url)
            data = response.json()

            # Log API consulta actual
            cursor.execute("""
                INSERT INTO ApiLog (idLog, endpoint, respuesta_json, fecha_hora)
                VALUES (apilog_seq.NEXTVAL, :1, :2, SYSDATE)
            """, [url, str(data)])
            conn.commit()

            if response.status_code == 200:
                nombre_ciudad = data['name']
                pais = data['sys']['country']
                temp = data['main']['temp']
                sensacion_termica = data['main']['feels_like']
                humedad = data['main']['humidity']
                viento = data['wind']['speed']
                condicion = data['weather'][0]['description']
                icono = data['weather'][0]['icon']
                lat = data['coord']['lat']
                lon = data['coord']['lon']

                # Buscar o insertar ciudad
                cursor.execute("""
                    SELECT idCiudad FROM Ciudad
                    WHERE LOWER(nombre) = LOWER(:1)
                      AND UPPER(pais) = UPPER(:2)
                """, [nombre_ciudad.lower(), pais.upper()])
                row = cursor.fetchone()

                if not row:
                    cursor.execute("""
                        INSERT INTO Ciudad (idCiudad, nombre, pais, lat, lon)
                        VALUES (ciudad_seq.NEXTVAL, :1, :2, :3, :4)
                    """, [nombre_ciudad, pais, lat, lon])
                    conn.commit()
                    cursor.execute("""
                        SELECT idCiudad FROM Ciudad
                        WHERE LOWER(nombre) = LOWER(:1)
                          AND UPPER(pais) = UPPER(:2)
                    """, [nombre_ciudad.lower(), pais.upper()])
                    row = cursor.fetchone()

                id_ciudad = row[0]

                # Insertar consulta usuario
                if request.user.is_authenticated:
                    try:
                        cursor.execute("""
                            INSERT INTO Consulta (idConsulta, idUsuario, idCiudad, fecha_hora)
                            VALUES (consulta_seq.NEXTVAL, :1, :2, SYSDATE)
                        """, [request.user.usuarioextendido.idusuario, id_ciudad])
                        conn.commit()
                    except Exception as e:
                        print("Error guardando consulta:", e)

                # Insertar registro clima
                try:
                    cursor.execute("""
                        INSERT INTO RegistroClima (idRegistro, idCiudad, temp, humedad, viento, fecha_hora)
                        VALUES (registroclima_seq.NEXTVAL, :1, :2, :3, :4, SYSDATE)
                    """, [id_ciudad, temp, humedad, viento])
                    conn.commit()
                except cx_Oracle.DatabaseError as e:
                    if e.args[0].code == 20001:
                        messages.warning(request, "El registro ya existe para hoy.")
                    else:
                        raise

                # Obtener idRegistro
                cursor.execute("""
                    SELECT MAX(idRegistro)
                    FROM RegistroClima
                    WHERE idCiudad = :1
                """, [id_ciudad])
                id_registro = cursor.fetchone()[0]

                # Insertar condición si no existe
                try:
                    cursor.execute("""
                        INSERT INTO Condicion (idCondicion, descripcion, icono)
                        VALUES (condicion_seq.NEXTVAL, :1, :2)
                    """, [condicion, icono])
                    conn.commit()
                except cx_Oracle.IntegrityError:
                    pass

                cursor.execute("""
                    SELECT idCondicion FROM Condicion
                    WHERE LOWER(descripcion) = LOWER(:1)
                """, [condicion.lower()])
                id_condicion = cursor.fetchone()[0]

                # Vincular condición
                cursor.execute("""
                    INSERT INTO ClimaCondicion (id, idRegistro, idCondicion)
                    VALUES (climacondicion_seq.NEXTVAL, :1, :2)
                """, [id_registro, id_condicion])
                conn.commit()

                # Temperatura media último mes
                cursor.execute("""
                    SELECT ROUND(AVG(temp), 2)
                    FROM RegistroClima
                    WHERE idCiudad = :1
                      AND fecha_hora >= ADD_MONTHS(SYSDATE, -1)
                """, [id_ciudad])
                temp_media = cursor.fetchone()[0]

                # --- Pronóstico ---
                forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?q={ciudad}&appid={API_KEY}&units=metric&lang=es'
                forecast_response = requests.get(forecast_url)
                forecast_data = forecast_response.json()

                # Log forecast
                cursor.execute("""
                    INSERT INTO ApiLog (idLog, endpoint, respuesta_json, fecha_hora)
                    VALUES (apilog_seq.NEXTVAL, :1, :2, SYSDATE)
                """, [forecast_url, str(forecast_data)])
                conn.commit()

                if forecast_response.status_code == 200:
                    cursor.execute("""
                        DELETE FROM PronosticoHora
                        WHERE idCiudad = :1 AND fecha_hora >= SYSDATE
                    """, [id_ciudad])

                    agrupados = defaultdict(list)

                    for item in forecast_data['list']:
                        dt = datetime.strptime(item['dt_txt'], "%Y-%m-%d %H:%M:%S")
                        temp_hora = item['main']['temp']
                        desc = item['weather'][0]['description']
                        icono_hora = item['weather'][0]['icon']
                        humedad = item['main']['humidity']
                        presion = item['main']['pressure']
                        viento = item['wind']['speed']
                        direccion = item['wind'].get('deg', '')

                        # Insertar en DB si quieres (aquí solo tienes temp y descripción)
                        cursor.execute("""
                            INSERT INTO PronosticoHora (
                                idPronostico, idCiudad, fecha_hora, temperatura, descripcion, icono
                            ) VALUES (
                                pronosticohora_seq.NEXTVAL, :1, :2, :3, :4, :5
                            )
                        """, [id_ciudad, dt, temp_hora, desc, icono_hora])

                        print(f"Insertado pronóstico: {dt}, {temp_hora}°C, {desc}")

                        # Construir pronóstico horario con más campos
                        pronostico.append({
                            'hora': item['dt_txt'],
                            'temp': round(temp_hora),
                            'icono': icono_hora,
                            'descripcion': desc.title(),
                            'humedad': humedad,
                            'presion': presion,
                            'viento': viento,
                            'direccion_viento': f"{direccion}°" if direccion != '' else 'N/A'
                        })

                        dia_str = dt.strftime("%A %d/%m")
                        agrupados[dia_str].append({
                            'temp': temp_hora,
                            'icono': icono_hora,
                            'descripcion': desc,
                            'humedad': humedad,
                            'presion': presion,
                            'viento': viento
                        })

                    conn.commit()

                    # Guardar fecha actualización
                    cursor.execute("""
                        DELETE FROM Configuracion WHERE clave = 'ultima_actualizacion'
                    """)
                    cursor.execute("""
                        INSERT INTO Configuracion (idConfig, clave, valor)
                        VALUES (configuracion_seq.NEXTVAL, 'ultima_actualizacion', :1)
                    """, [datetime.now().strftime("%d/%m/%Y %H:%M:%S")])
                    conn.commit()

                    # Construir pronóstico diario con medias
                    for dia, entradas in list(agrupados.items())[:7]:
                        temps = [e['temp'] for e in entradas]
                        humedades = [e['humedad'] for e in entradas]
                        presiones = [e['presion'] for e in entradas]
                        vientos = [e['viento'] for e in entradas]

                        pronostico_diario.append({
                            'fecha': dia,
                            'temp_max': round(max(temps)),
                            'temp_min': round(min(temps)),
                            'icono': entradas[0]['icono'],
                            'descripcion': entradas[0]['descripcion'].title(),
                            'humedad': round(sum(humedades) / len(humedades)),
                            'presion': round(sum(presiones) / len(presiones)),
                            'viento': round(sum(vientos) / len(vientos), 1)
                        })

                datos = {
                    'ciudad': nombre_ciudad,
                    'pais': pais,
                    'temperatura': round(temp),
                    'humedad': humedad,
                    'viento': viento,
                    'condicion': condicion.title(),
                    'icono': icono,
                    'temp_media': temp_media,
                    'sensacion_termica': round(sensacion_termica)
                }

            else:
                error = data.get('message', 'Error en la API')

        except Exception as e:
            error = f"Ocurrió un error: {e}"
            print(">>> ERROR:", e)

        finally:
            cursor.close()
            conn.close()

    return render(request, 'tiempo/temperatura.html', {
        'datos': datos,
        'error': error,
        'pronostico': pronostico,
        'pronostico_diario': pronostico_diario
    })

def registro(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("info_clima")
    else:
        form = RegistroUsuarioForm()

    return render(request, "usuario/registro.html", {"form": form})


@login_required
def favoritas(request):
    conn = get_connection()
    cursor = conn.cursor()
    user_id = request.user.usuarioextendido.idusuario

    if request.method == "POST":
        ciudad = request.POST.get("ciudad")
        if ciudad:
            try:
                # Buscar la ciudad
                print(f">>> Buscando ciudad '{ciudad}' en la tabla Ciudad...")
                cursor.execute("""
                    SELECT idCiudad FROM Ciudad
                    WHERE LOWER(nombre) = LOWER(:1)
                """, [ciudad.lower()])
                row = cursor.fetchone()

                if row:
                    id_ciudad = row[0]
                    try:
                        print(f">>> Insertando ciudad favorita: IDUSUARIO={user_id}, IDCIUDAD={id_ciudad}")
                        cursor.execute("""
                            INSERT INTO CiudadFavorita (IDUSUARIO, IDCIUDAD, FECHA_AGREGADO)
                            VALUES (:1, :2, SYSDATE)
                        """, [user_id, id_ciudad])
                        conn.commit()
                        print(">>> Commit realizado correctamente.")
                        messages.success(request, f"{ciudad.title()} añadida a tus favoritas.")
                    except cx_Oracle.IntegrityError as e:
                        messages.warning(request, f"{ciudad.title()} ya estaba en tus favoritas.")
                        print(">>> IntegrityError:", e)
                    except Exception as e:
                        messages.error(request, f"Error al insertar favorita: {e}")
                        print(">>> Otro error al insertar:", e)
                else:
                    messages.error(request, f"No se encontró la ciudad '{ciudad}'. Por favor verifica el nombre.")
                    print(">>> La ciudad no existe en la tabla Ciudad.")

            except Exception as e:
                messages.error(request, f"Error consultando ciudad: {e}")
                print(">>> Error consultando ciudad:", e)

        return redirect('favoritas')

    # Mostrar favoritas
    try:
        print(f">>> Obteniendo ciudades favoritas del usuario {user_id}")
        cursor.execute("""
            SELECT c.idCiudad, c.nombre, c.pais
            FROM Ciudad c
            JOIN CiudadFavorita uf ON c.idCiudad = uf.idCiudad
            WHERE uf.idUsuario = :1
        """, [user_id])

        favoritas = cursor.fetchall()
        print(f">>> Favoritas encontradas: {favoritas}")
    except Exception as e:
        messages.error(request, f"Error obteniendo favoritas: {e}")
        print(">>> Error obteniendo favoritas:", e)
        favoritas = []

    cursor.close()
    conn.close()

    return render(request, "usuario/favorita.html", {"favoritas": favoritas})

@login_required
def eliminar_favorita(request, id):
    conn = get_connection()
    cursor = conn.cursor()
    user_id = request.user.usuarioextendido.idusuario

    try:
        cursor.execute("""
            DELETE FROM CiudadFavorita
            WHERE idUsuario = :1 AND idCiudad = :2
        """, [user_id, id])
        conn.commit()
        messages.success(request, "Ciudad favorita eliminada correctamente.")
    except Exception as e:
        messages.error(request, f"Error eliminando favorita: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect('favoritas')


def cerrar_sesion(request):
    logout(request)
    return render(request, "registrarse/cerrar_sesion.html")

def sobre_proyecto(request):
    return render(request, "tiempo/sobre.html")

def contacto(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        email = request.POST.get("email")
        mensaje = request.POST.get("mensaje")

        # Aquí puedes enviar un correo si quieres:
        # send_mail(
        #     subject=f"Mensaje de {nombre}",
        #     message=mensaje,
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=[settings.DEFAULT_FROM_EMAIL],
        # )

        messages.success(request, "Tu mensaje ha sido enviado correctamente.")
        return redirect('contacto')

    return render(request, "tiempo/contacto.html")


@staff_member_required
def ver_logs(request):
    conn = get_connection()
    cursor = conn.cursor()
    logs = []
    try:
        cursor.execute("""
            SELECT idlog, endpoint, TO_CHAR(fecha_hora, 'DD/MM/YYYY HH24:MI'), respuesta_json
            FROM ApiLog
            ORDER BY fecha_hora DESC
        """)
        raw_logs = cursor.fetchall()

        # Convertir cada fila a tupla con el CLOB leído como string
        logs = []
        for row in raw_logs:
            idlog, endpoint, fecha, resp_clob = row
            # Leer máximo 200 caracteres para no saturar
            if resp_clob is not None:
                resp_text = resp_clob.read()[:200]
            else:
                resp_text = ""
            logs.append((idlog, endpoint, fecha, resp_text))

    finally:
        cursor.close()
        conn.close()

    return render(request, "admin_custom/ver_logs.html", {"logs": logs})

@staff_member_required
def limpiar_logs(request):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM ApiLog")
        conn.commit()
        messages.success(request, "Todos los logs han sido eliminados.")
    except Exception as e:
        messages.error(request, f"Error al eliminar logs: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect("ver_logs")