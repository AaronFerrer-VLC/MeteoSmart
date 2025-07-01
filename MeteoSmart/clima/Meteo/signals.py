import os
from dotenv import load_dotenv

load_dotenv()

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UsuarioExtendido
import cx_Oracle

logger = logging.getLogger(__name__)

def get_connection():
    user = os.getenv("ORACLE_USER")
    password = os.getenv("ORACLE_PASSWORD")
    dsn = os.getenv("ORACLE_DSN")

    if not all([user, password, dsn]):
        raise ValueError("Faltan variables de entorno para la conexión a Oracle.")

    return cx_Oracle.connect(user, password, dsn)


@receiver(post_save, sender=User)
def crear_usuario_extendido(sender, instance, created, **kwargs):
    if created:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Usuario (idUsuario, nombre, email, ciudad_favorita)
                VALUES (usuario_seq.NEXTVAL, :1, :2, NULL)
            """, [instance.username, instance.email])
            conn.commit()

            cursor.execute("SELECT usuario_seq.CURRVAL FROM dual")
            id_oracle = cursor.fetchone()[0]

            UsuarioExtendido.objects.create(user=instance, idusuario=id_oracle)

        except Exception as e:
            logger.error(f"Error insertando en Oracle: {e}")
            raise

        finally:
            cursor.close()
            conn.close()
