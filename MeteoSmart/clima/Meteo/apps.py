from django.apps import AppConfig

class ClimaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Meteo'

    def ready(self):
        from . import signals
