from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UsuarioExtendido
import cx_Oracle

def get_connection():
    return cx_Oracle.connect("system", "pythonoracle", "localhost/XE")

@receiver(post_save, sender=User)
def crear_usuario_extendido(sender, instance, created, **kwargs):
    if created:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Insertar en Oracle
            cursor.execute("""
                INSERT INTO Usuario (idUsuario, nombre, email, ciudad_favorita)
                VALUES (usuario_seq.NEXTVAL, :1, :2, NULL)
            """, [instance.username, instance.email])
            conn.commit()

            cursor.execute("SELECT usuario_seq.CURRVAL FROM dual")
            id_oracle = cursor.fetchone()[0]

            # Crear el UsuarioExtendido
            UsuarioExtendido.objects.create(user=instance, idusuario=id_oracle)
        finally:
            cursor.close()
            conn.close()
