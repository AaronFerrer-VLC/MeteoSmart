"""
Views for the Meteo application.

This module contains all view functions for handling HTTP requests,
including weather API integration, user management, and data display.
"""
import os
import logging
import requests
import cx_Oracle
from collections import defaultdict
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from dotenv import load_dotenv

from .forms import RegistroUsuarioForm
from .models import UsuarioExtendido
from .utils import get_oracle_connection, validate_city_name

load_dotenv()

logger = logging.getLogger(__name__)
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")


@login_required
def historial(request):
    """
    Display weather query history for the authenticated user.
    
    Retrieves the user's query history from Oracle database and displays
    it in a table format.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered template with query history
    """
    user_id = request.user.usuarioextendido.idusuario
    
    if not user_id:
        messages.error(request, "No se encontró tu ID de usuario. Por favor, contacta al administrador.")
        return redirect('info_clima')
    
    logger.debug(f"Obteniendo historial para usuario ID: {user_id}")
    
    registros = []
    try:
        with get_oracle_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.nombre, c.pais, TO_CHAR(con.fecha_hora, 'DD/MM/YYYY HH24:MI:SS')
                FROM Consulta con
                JOIN Ciudad c ON c.idCiudad = con.idCiudad
                WHERE con.idUsuario = :1
                ORDER BY con.fecha_hora DESC
            """, [user_id])
            registros = cursor.fetchall()
            logger.info(f"Historial obtenido: {len(registros)} registros")
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}", exc_info=True)
        messages.error(request, "Error al obtener el historial. Por favor, intenta más tarde.")
    
    return render(request, "usuario/historial.html", {
        "registros": registros
    })


def clima_api(request):
    """
    Main weather API view.
    
    Handles weather queries, fetches data from OpenWeatherMap API,
    stores data in Oracle database, and displays weather information
    with hourly and daily forecasts.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered template with weather data
    """
    ciudad = request.GET.get('ciudad', '').strip()
    datos = {}
    error = None
    pronostico = []
    pronostico_diario = []
    
    if not ciudad:
        return render(request, 'tiempo/temperatura.html', {
            'datos': datos,
            'error': error,
            'pronostico': pronostico,
            'pronostico_diario': pronostico_diario
        })
    
    # Validate city name
    if not validate_city_name(ciudad):
        error = "Nombre de ciudad inválido. Por favor, introduce un nombre válido."
        return render(request, 'tiempo/temperatura.html', {
            'datos': datos,
            'error': error,
            'pronostico': pronostico,
            'pronostico_diario': pronostico_diario
        })
    
    try:
        # Fetch current weather
        url = f'https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={API_KEY}&units=metric&lang=es'
        
        if not API_KEY:
            error = "Error de configuración: API key no encontrada."
            logger.error("OPENWEATHERMAP_API_KEY no configurada")
            return render(request, 'tiempo/temperatura.html', {
                'datos': datos,
                'error': error,
                'pronostico': pronostico,
                'pronostico_diario': pronostico_diario
            })
        
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Log API request
        try:
            with get_oracle_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO ApiLog (idLog, endpoint, respuesta_json, fecha_hora)
                    VALUES (apilog_seq.NEXTVAL, :1, :2, SYSDATE)
                """, [url, str(data)[:4000]])  # Limit response size
                conn.commit()
        except Exception as e:
            logger.warning(f"Error guardando log de API: {e}")
        
        if response.status_code != 200:
            error = data.get('message', 'Error al consultar la API del clima.')
            logger.warning(f"Error en API OpenWeatherMap: {error}")
            return render(request, 'tiempo/temperatura.html', {
                'datos': datos,
                'error': error,
                'pronostico': pronostico,
                'pronostico_diario': pronostico_diario
            })
        
        # Extract weather data
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
        
        # Process database operations
        with get_oracle_connection() as conn:
            cursor = conn.cursor()
            
            # Find or create city
            id_ciudad = _get_or_create_ciudad(cursor, conn, nombre_ciudad, pais, lat, lon)
            
            # Save user query if authenticated
            if request.user.is_authenticated:
                _save_user_query(cursor, conn, request.user, id_ciudad)
            
            # Save weather record
            id_registro = _save_weather_record(cursor, conn, id_ciudad, temp, humedad, viento, condicion, icono)
            
            # Calculate average temperature
            temp_media = _get_average_temperature(cursor, id_ciudad)
            
            # Fetch and process forecast
            pronostico, pronostico_diario = _process_forecast(
                cursor, conn, ciudad, id_ciudad, API_KEY
            )
            
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
    
    except requests.RequestException as e:
        error = f"Error de conexión con la API del clima: {str(e)}"
        logger.error(f"Error de conexión API: {e}", exc_info=True)
    except KeyError as e:
        error = "Error procesando los datos del clima. Por favor, intenta más tarde."
        logger.error(f"Error procesando datos API: {e}", exc_info=True)
    except Exception as e:
        error = f"Ocurrió un error inesperado: {str(e)}"
        logger.error(f"Error inesperado en clima_api: {e}", exc_info=True)
    
    return render(request, 'tiempo/temperatura.html', {
        'datos': datos,
        'error': error,
        'pronostico': pronostico,
        'pronostico_diario': pronostico_diario
    })


def _get_or_create_ciudad(cursor, conn, nombre_ciudad, pais, lat, lon):
    """Helper function to get or create a city in the database."""
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
    
    return row[0] if row else None


def _save_user_query(cursor, conn, user, id_ciudad):
    """Helper function to save user query to database."""
    try:
        user_id = user.usuarioextendido.idusuario
        if user_id:
            cursor.execute("""
                INSERT INTO Consulta (idConsulta, idUsuario, idCiudad, fecha_hora)
                VALUES (consulta_seq.NEXTVAL, :1, :2, SYSDATE)
            """, [user_id, id_ciudad])
            conn.commit()
    except Exception as e:
        logger.warning(f"Error guardando consulta de usuario: {e}")


def _save_weather_record(cursor, conn, id_ciudad, temp, humedad, viento, condicion, icono):
    """Helper function to save weather record to database."""
    try:
        cursor.execute("""
            INSERT INTO RegistroClima (idRegistro, idCiudad, temp, humedad, viento, fecha_hora)
            VALUES (registroclima_seq.NEXTVAL, :1, :2, :3, :4, SYSDATE)
        """, [id_ciudad, temp, humedad, viento])
        conn.commit()
    except cx_Oracle.DatabaseError as e:
        if e.args[0].code == 20001:
            logger.info("El registro ya existe para hoy.")
        else:
            logger.error(f"Error guardando registro clima: {e}")
            raise
    
    # Get registro ID
    cursor.execute("""
        SELECT MAX(idRegistro)
        FROM RegistroClima
        WHERE idCiudad = :1
    """, [id_ciudad])
    id_registro = cursor.fetchone()[0]
    
    # Save condition
    try:
        cursor.execute("""
            INSERT INTO Condicion (idCondicion, descripcion, icono)
            VALUES (condicion_seq.NEXTVAL, :1, :2)
        """, [condicion, icono])
        conn.commit()
    except cx_Oracle.IntegrityError:
        pass  # Condition already exists
    
    cursor.execute("""
        SELECT idCondicion FROM Condicion
        WHERE LOWER(descripcion) = LOWER(:1)
    """, [condicion.lower()])
    id_condicion = cursor.fetchone()[0]
    
    # Link condition
    cursor.execute("""
        INSERT INTO ClimaCondicion (id, idRegistro, idCondicion)
        VALUES (climacondicion_seq.NEXTVAL, :1, :2)
    """, [id_registro, id_condicion])
    conn.commit()
    
    return id_registro


def _get_average_temperature(cursor, id_ciudad):
    """Helper function to get average temperature for the last month."""
    try:
        cursor.execute("""
            SELECT ROUND(AVG(temp), 2)
            FROM RegistroClima
            WHERE idCiudad = :1
              AND fecha_hora >= ADD_MONTHS(SYSDATE, -1)
        """, [id_ciudad])
        result = cursor.fetchone()
        return result[0] if result and result[0] else None
    except Exception as e:
        logger.warning(f"Error obteniendo temperatura media: {e}")
        return None


def _process_forecast(cursor, conn, ciudad, id_ciudad, api_key):
    """Helper function to fetch and process weather forecast."""
    pronostico = []
    pronostico_diario = []
    
    try:
        forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?q={ciudad}&appid={api_key}&units=metric&lang=es'
        forecast_response = requests.get(forecast_url, timeout=10)
        forecast_data = forecast_response.json()
        
        # Log forecast request
        try:
            cursor.execute("""
                INSERT INTO ApiLog (idLog, endpoint, respuesta_json, fecha_hora)
                VALUES (apilog_seq.NEXTVAL, :1, :2, SYSDATE)
            """, [forecast_url, str(forecast_data)[:4000]])
            conn.commit()
        except Exception as e:
            logger.warning(f"Error guardando log de pronóstico: {e}")
        
        if forecast_response.status_code != 200:
            logger.warning(f"Error en pronóstico: {forecast_data.get('message', 'Unknown error')}")
            return pronostico, pronostico_diario
        
        # Clear old forecasts
        cursor.execute("""
            DELETE FROM PronosticoHora
            WHERE idCiudad = :1 AND fecha_hora >= SYSDATE
        """, [id_ciudad])
        
        agrupados = defaultdict(list)
        
        for item in forecast_data.get('list', []):
            dt = datetime.strptime(item['dt_txt'], "%Y-%m-%d %H:%M:%S")
            temp_hora = item['main']['temp']
            desc = item['weather'][0]['description']
            icono_hora = item['weather'][0]['icon']
            humedad = item['main']['humidity']
            presion = item['main']['pressure']
            viento = item['wind']['speed']
            direccion = item['wind'].get('deg', '')
            
            # Save to database
            try:
                cursor.execute("""
                    INSERT INTO PronosticoHora (
                        idPronostico, idCiudad, fecha_hora, temperatura, descripcion, icono
                    ) VALUES (
                        pronosticohora_seq.NEXTVAL, :1, :2, :3, :4, :5
                    )
                """, [id_ciudad, dt, temp_hora, desc, icono_hora])
            except Exception as e:
                logger.warning(f"Error guardando pronóstico hora: {e}")
            
            # Build hourly forecast
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
            
            # Group by day
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
        
        # Build daily forecast
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
        
        # Save last update time
        try:
            cursor.execute("DELETE FROM Configuracion WHERE clave = 'ultima_actualizacion'")
            cursor.execute("""
                INSERT INTO Configuracion (idConfig, clave, valor)
                VALUES (configuracion_seq.NEXTVAL, 'ultima_actualizacion', :1)
            """, [datetime.now().strftime("%d/%m/%Y %H:%M:%S")])
            conn.commit()
        except Exception as e:
            logger.warning(f"Error guardando última actualización: {e}")
    
    except Exception as e:
        logger.error(f"Error procesando pronóstico: {e}", exc_info=True)
    
    return pronostico, pronostico_diario


def registro(request):
    """
    User registration view.
    
    Handles user registration form submission and creates new user accounts.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered registration form or redirect after successful registration
    """
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"¡Bienvenido, {user.username}! Tu cuenta ha sido creada exitosamente.")
            logger.info(f"Nuevo usuario registrado: {user.username}")
            return redirect("info_clima")
    else:
        form = RegistroUsuarioForm()
    
    return render(request, "usuario/registro.html", {"form": form})


@login_required
def favoritas(request):
    """
    Manage favorite cities view.
    
    Allows users to add and view their favorite cities.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered template with favorite cities
    """
    user_id = request.user.usuarioextendido.idusuario
    
    if not user_id:
        messages.error(request, "No se encontró tu ID de usuario. Por favor, contacta al administrador.")
        return redirect('info_clima')
    
    if request.method == "POST":
        ciudad = request.POST.get("ciudad", "").strip()
        
        if not ciudad:
            messages.error(request, "Por favor, introduce un nombre de ciudad válido.")
            return redirect('favoritas')
        
        if not validate_city_name(ciudad):
            messages.error(request, "Nombre de ciudad inválido. Por favor, verifica el nombre.")
            return redirect('favoritas')
        
        try:
            with get_oracle_connection() as conn:
                cursor = conn.cursor()
                
                # Find city
                cursor.execute("""
                    SELECT idCiudad FROM Ciudad
                    WHERE LOWER(nombre) = LOWER(:1)
                """, [ciudad.lower()])
                row = cursor.fetchone()
                
                if row:
                    id_ciudad = row[0]
                    try:
                        cursor.execute("""
                            INSERT INTO CiudadFavorita (IDUSUARIO, IDCIUDAD, FECHA_AGREGADO)
                            VALUES (:1, :2, SYSDATE)
                        """, [user_id, id_ciudad])
                        conn.commit()
                        messages.success(request, f"{ciudad.title()} añadida a tus favoritas.")
                        logger.info(f"Ciudad favorita añadida: {ciudad} para usuario {user_id}")
                    except cx_Oracle.IntegrityError:
                        messages.warning(request, f"{ciudad.title()} ya estaba en tus favoritas.")
                    except Exception as e:
                        logger.error(f"Error insertando favorita: {e}")
                        messages.error(request, "Error al añadir la ciudad favorita.")
                else:
                    messages.error(
                        request,
                        f"No se encontró la ciudad '{ciudad}'. "
                        "Primero busca la ciudad en la página principal."
                    )
        except Exception as e:
            logger.error(f"Error consultando ciudad: {e}", exc_info=True)
            messages.error(request, "Error al procesar la solicitud. Por favor, intenta más tarde.")
        
        return redirect('favoritas')
    
    # Display favorites
    favoritas_list = []
    try:
        with get_oracle_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.idCiudad, c.nombre, c.pais
                FROM Ciudad c
                JOIN CiudadFavorita uf ON c.idCiudad = uf.idCiudad
                WHERE uf.idUsuario = :1
                ORDER BY c.nombre
            """, [user_id])
            favoritas_list = cursor.fetchall()
    except Exception as e:
        logger.error(f"Error obteniendo favoritas: {e}", exc_info=True)
        messages.error(request, "Error al obtener las ciudades favoritas.")
    
    return render(request, "usuario/favorita.html", {"favoritas": favoritas_list})


@login_required
def eliminar_favorita(request, id):
    """
    Delete favorite city view.
    
    Removes a city from the user's favorites list.
    
    Args:
        request: HTTP request object
        id: City ID to remove
        
    Returns:
        HttpResponse: Redirect to favorites page
    """
    user_id = request.user.usuarioextendido.idusuario
    
    if not user_id:
        messages.error(request, "No se encontró tu ID de usuario.")
        return redirect('favoritas')
    
    try:
        with get_oracle_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM CiudadFavorita
                WHERE idUsuario = :1 AND idCiudad = :2
            """, [user_id, id])
            conn.commit()
            messages.success(request, "Ciudad favorita eliminada correctamente.")
            logger.info(f"Ciudad favorita eliminada: ID {id} para usuario {user_id}")
    except Exception as e:
        logger.error(f"Error eliminando favorita: {e}", exc_info=True)
        messages.error(request, "Error al eliminar la ciudad favorita.")
    
    return redirect('favoritas')


def cerrar_sesion(request):
    """
    Logout view.
    
    Handles user logout and displays logout confirmation.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered logout confirmation page
    """
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return render(request, "registrarse/cerrar_sesion.html")


def sobre_proyecto(request):
    """
    About project view.
    
    Displays information about the MeteoSmart project.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered about page
    """
    return render(request, "tiempo/sobre.html")


def contacto(request):
    """
    Contact view.
    
    Handles contact form submissions.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered contact form or redirect after submission
    """
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        email = request.POST.get("email", "").strip()
        mensaje = request.POST.get("mensaje", "").strip()
        
        # Basic validation
        if not all([nombre, email, mensaje]):
            messages.error(request, "Por favor, completa todos los campos.")
            return render(request, "tiempo/contacto.html")
        
        # Email validation
        if '@' not in email:
            messages.error(request, "Por favor, introduce un email válido.")
            return render(request, "tiempo/contacto.html")
        
        # Here you could send an email
        # send_mail(
        #     subject=f"Mensaje de {nombre}",
        #     message=mensaje,
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=[settings.DEFAULT_FROM_EMAIL],
        # )
        
        logger.info(f"Mensaje de contacto recibido de {nombre} ({email})")
        messages.success(request, "Tu mensaje ha sido enviado correctamente. Te responderemos pronto.")
        return redirect('contacto')
    
    return render(request, "tiempo/contacto.html")


@staff_member_required
def ver_logs(request):
    """
    View API logs (staff only).
    
    Displays API request logs from the database.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered logs page
    """
    logs = []
    try:
        with get_oracle_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT idlog, endpoint, TO_CHAR(fecha_hora, 'DD/MM/YYYY HH24:MI'), respuesta_json
                FROM ApiLog
                ORDER BY fecha_hora DESC
            """)
            raw_logs = cursor.fetchall()
            
            # Convert CLOB to string
            for row in raw_logs:
                idlog, endpoint, fecha, resp_clob = row
                if resp_clob is not None:
                    try:
                        resp_text = resp_clob.read()[:200] if hasattr(resp_clob, 'read') else str(resp_clob)[:200]
                    except Exception:
                        resp_text = str(resp_clob)[:200]
                else:
                    resp_text = ""
                logs.append((idlog, endpoint, fecha, resp_text))
    except Exception as e:
        logger.error(f"Error obteniendo logs: {e}", exc_info=True)
        messages.error(request, "Error al obtener los logs.")
    
    return render(request, "admin_custom/ver_logs.html", {"logs": logs})


@staff_member_required
def limpiar_logs(request):
    """
    Clear API logs (staff only).
    
    Deletes all API logs from the database.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Redirect to logs page
    """
    try:
        with get_oracle_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ApiLog")
            conn.commit()
            messages.success(request, "Todos los logs han sido eliminados.")
            logger.info("Logs eliminados por usuario staff")
    except Exception as e:
        logger.error(f"Error eliminando logs: {e}", exc_info=True)
        messages.error(request, "Error al eliminar los logs.")
    
    return redirect("ver_logs")
