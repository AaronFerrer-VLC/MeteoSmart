from django.db import models
from django import forms

from django.contrib.auth.models import User

class UsuarioExtendido(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ciudad_favorita = models.CharField(max_length=100, null=True, blank=True)
    idusuario = models.IntegerField(null=True, blank=True)  # ID de Oracle

    def __str__(self):
        return self.user.username


class FavoritaForm(forms.Form):
    ciudad = forms.CharField(
        label="Ciudad",
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Ciudad favorita'})
    )
class Configuracion(models.Model):
    idconfig = models.AutoField(primary_key=True)
    clave = models.CharField(max_length=100)
    valor = models.CharField(max_length=500)

    class Meta:
        managed = False
        db_table = 'Configuracion'

    def __str__(self):
        return self.clave

class ApiLog(models.Model):
    idlog = models.AutoField(primary_key=True)
    endpoint = models.CharField(max_length=500)
    respuesta_json = models.TextField()
    fecha_hora = models.DateTimeField()

    class Meta:
        managed = False  # Si la tabla la tienes en Oracle, no generes migraciones
        db_table = 'ApiLog'

    def __str__(self):
        return f"{self.endpoint} ({self.fecha_hora})"