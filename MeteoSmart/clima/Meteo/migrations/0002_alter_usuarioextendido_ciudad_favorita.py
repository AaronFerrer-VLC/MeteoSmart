# Generated by Django 5.2.3 on 2025-06-26 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Meteo', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuarioextendido',
            name='ciudad_favorita',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
