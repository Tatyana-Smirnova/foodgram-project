# Generated by Django 3.0.8 on 2020-12-08 23:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20201208_2251'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='slug',
        ),
    ]
