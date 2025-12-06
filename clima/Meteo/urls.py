"""
URL configuration for Meteo application.

This module defines all URL patterns for the Meteo app.
"""
from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    # Main weather view
    path('', views.clima_api, name='info_clima'),
    
    # Authentication
    path('registro/', views.registro, name='registro'),
    path('accounts/login/', LoginView.as_view(template_name='registrarse/iniciar_sesion.html'), name='login'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    
    # User features
    path('historial/', views.historial, name='historial'),
    path('favoritas/', views.favoritas, name='favoritas'),
    path('favoritas/eliminar/<int:id>/', views.eliminar_favorita, name='eliminar_favorita'),
    
    # Information pages
    path('contacto/', views.contacto, name='contacto'),
    path('sobre/', views.sobre_proyecto, name='sobre_proyecto'),
    
    # Admin features
    path('admin/logs/', views.ver_logs, name='ver_logs'),
    path('admin/logs/limpiar/', views.limpiar_logs, name='limpiar_logs'),
]


