# Generated by Django 3.2.3 on 2023-09-22 17:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20230922_1248'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscribe',
            options={'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
    ]
