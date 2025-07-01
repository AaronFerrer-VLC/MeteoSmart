from django.contrib import admin
from django import forms

from .models import UsuarioExtendido

# ---- UsuarioExtendido ----
@admin.register(UsuarioExtendido)
class UsuarioExtendidoAdmin(admin.ModelAdmin):
    list_display = ("user", "idusuario", "ciudad_favorita")
    search_fields = ("user__username",)

