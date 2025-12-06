"""
Signal handlers for the Meteo application.

This module contains Django signal receivers for automatic actions
when certain model events occur.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UsuarioExtendido
from .utils import get_oracle_connection

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def crear_usuario_extendido(sender, instance, created, **kwargs):
    """
    Signal receiver to create extended user profile when a new User is created.
    
    Creates a corresponding record in Oracle database and links it with
    UsuarioExtendido model.
    
    Args:
        sender: The model class (User)
        instance: The actual instance being saved
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    """
    if created:
        try:
            with get_oracle_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Usuario (idUsuario, nombre, email, ciudad_favorita)
                    VALUES (usuario_seq.NEXTVAL, :1, :2, NULL)
                """, [instance.username, instance.email or ''])
                conn.commit()
                
                cursor.execute("SELECT usuario_seq.CURRVAL FROM dual")
                id_oracle = cursor.fetchone()[0]
                
                UsuarioExtendido.objects.create(user=instance, idusuario=id_oracle)
                logger.info(f"Usuario extendido creado para {instance.username} (ID Oracle: {id_oracle})")
        
        except Exception as e:
            logger.error(f"Error insertando usuario en Oracle: {e}", exc_info=True)
            # Don't raise to avoid blocking user creation
            # The user will be created but without Oracle link
