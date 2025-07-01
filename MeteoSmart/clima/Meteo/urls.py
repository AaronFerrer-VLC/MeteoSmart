from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('', views.clima_api, name='info_clima'),
    path('registro/', views.registro, name='registro'),
    path('historial/', views.historial, name='historial'),
    path('favoritas/', views.favoritas, name='favoritas'),
    path('favoritas/eliminar/<int:id>/', views.eliminar_favorita, name='eliminar_favorita'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('contacto/', views.contacto, name='contacto'),
    path('sobre/', views.sobre_proyecto, name='sobre_proyecto'),
    path('accounts/login/',LoginView.as_view(template_name='registrarse/iniciar_sesion.html'),name='login'),
    path("admin/logs/", views.ver_logs, name="ver_logs"),
    path("admin/logs/", views.ver_logs, name="ver_logs"),
    path("admin/logs/limpiar/", views.limpiar_logs, name="limpiar_logs"),
]


