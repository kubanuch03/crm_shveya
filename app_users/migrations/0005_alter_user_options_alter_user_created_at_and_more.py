# Generated by Django 5.1.3 on 2024-12-19 18:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_users', '0004_filial_user_phone_number_user_telegram_user_whatsapp_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создание'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, max_length=255, null=True, verbose_name='Почта'),
        ),
        migrations.AlterField(
            model_name='user',
            name='filial',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app_users.filial', verbose_name='Филиал'),
        ),
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/employees/%Y/%m/%d/', verbose_name='Фото'),
        ),
        migrations.AlterField(
            model_name='user',
            name='modified_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Тзменено'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, max_length=14, null=True, verbose_name='Номер Телефона'),
        ),
        migrations.AlterField(
            model_name='user',
            name='telegram',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Телеграм'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=255, unique=True, verbose_name='Псевдоним'),
        ),
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.CharField(blank=True, null=True, unique=True, verbose_name='UUiD'),
        ),
        migrations.AlterField(
            model_name='user',
            name='whatsapp',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='WhatsApp'),
        ),
    ]
