# Generated by Django 5.1.3 on 2025-06-14 10:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app_productions', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='processstage',
            name='assigned_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_process_stages', to=settings.AUTH_USER_MODEL, verbose_name='Ответственный/Исполнитель'),
        ),
        migrations.AddField(
            model_name='processstage',
            name='batch_product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='process_stages_in_batch', to='app_productions.batchproduct', verbose_name='Товар в партии'),
        ),
        migrations.AddField(
            model_name='processstage',
            name='confirmed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='confirmed_stages', to=settings.AUTH_USER_MODEL, verbose_name='Подтвердил'),
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ManyToManyField(blank=True, to='app_productions.category', verbose_name='Категория'),
        ),
        migrations.AddField(
            model_name='product',
            name='color',
            field=models.ManyToManyField(blank=True, to='app_productions.color', verbose_name='Цвет'),
        ),
        migrations.AddField(
            model_name='processstage',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='direct_process_stages', to='app_productions.product', verbose_name='Товар'),
        ),
        migrations.AddField(
            model_name='batchproduct',
            name='product',
            field=models.ManyToManyField(to='app_productions.product', verbose_name='Товар'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_model',
            field=models.ManyToManyField(blank=True, to='app_productions.product_model', verbose_name='Модель'),
        ),
        migrations.AddField(
            model_name='batchproduct',
            name='batch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products_in_batch', to='app_productions.productionbatch', verbose_name='Партия'),
        ),
        migrations.AddField(
            model_name='productoperationrate',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='operation_rates', to='app_productions.product', verbose_name='Товар'),
        ),
        migrations.AddField(
            model_name='product',
            name='size',
            field=models.ManyToManyField(blank=True, to='app_productions.size', verbose_name='Размер '),
        ),
        migrations.AddField(
            model_name='worklog',
            name='stage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_logs', to='app_productions.processstage', verbose_name='Этап процесса'),
        ),
        migrations.AddField(
            model_name='worklog',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='work_logs', to=settings.AUTH_USER_MODEL, verbose_name='Сотрудник'),
        ),
        migrations.AlterUniqueTogether(
            name='batchproduct',
            unique_together={('batch',)},
        ),
        migrations.AlterUniqueTogether(
            name='productoperationrate',
            unique_together={('product', 'operation_type')},
        ),
    ]
