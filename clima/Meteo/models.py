"""
Models for the Meteo application.

This module defines the database models used in the application,
including user extensions, configuration, and API logging.
"""
from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator


class UsuarioExtendido(models.Model):
    """
    Extended user profile model.
    
    Stores additional user information linked to the Django User model
    and maintains synchronization with Oracle database.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='usuarioextendido',
        verbose_name='Usuario'
    )
    ciudad_favorita = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Ciudad Favorita',
        help_text='Ciudad favorita del usuario'
    )
    idusuario = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='ID Usuario Oracle',
        help_text='ID del usuario en la base de datos Oracle'
    )

    class Meta:
        verbose_name = 'Usuario Extendido'
        verbose_name_plural = 'Usuarios Extendidos'
        ordering = ['user__username']

    def __str__(self):
        return f"{self.user.username} - {self.ciudad_favorita or 'Sin ciudad favorita'}"


class FavoritaForm(forms.Form):
    """Form for adding favorite cities."""
    ciudad = forms.CharField(
        label="Ciudad",
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ciudad favorita',
            'class': 'form-control'
        }),
        validators=[MinLengthValidator(2)]
    )


class Configuracion(models.Model):
    """
    Configuration model for storing key-value settings.
    
    This model maps to an Oracle database table and is not managed by Django migrations.
    """
    idconfig = models.AutoField(primary_key=True, verbose_name='ID Configuración')
    clave = models.CharField(
        max_length=100,
        verbose_name='Clave',
        help_text='Nombre de la configuración'
    )
    valor = models.CharField(
        max_length=500,
        verbose_name='Valor',
        help_text='Valor de la configuración'
    )

    class Meta:
        managed = False
        db_table = 'Configuracion'
        verbose_name = 'Configuración'
        verbose_name_plural = 'Configuraciones'
        ordering = ['clave']

    def __str__(self):
        return f"{self.clave}: {self.valor}"


class ApiLog(models.Model):
    """
    API logging model for tracking API requests and responses.
    
    This model maps to an Oracle database table and is not managed by Django migrations.
    """
    idlog = models.AutoField(primary_key=True, verbose_name='ID Log')
    endpoint = models.CharField(
        max_length=500,
        verbose_name='Endpoint',
        help_text='URL del endpoint de la API'
    )
    respuesta_json = models.TextField(
        verbose_name='Respuesta JSON',
        help_text='Respuesta de la API en formato JSON'
    )
    fecha_hora = models.DateTimeField(
        verbose_name='Fecha y Hora',
        help_text='Fecha y hora de la petición'
    )

    class Meta:
        managed = False
        db_table = 'ApiLog'
        verbose_name = 'Log de API'
        verbose_name_plural = 'Logs de API'
        ordering = ['-fecha_hora']
        get_latest_by = 'fecha_hora'

    def __str__(self):
        return f"{self.endpoint} ({self.fecha_hora})"