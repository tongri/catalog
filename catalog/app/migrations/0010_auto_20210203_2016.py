# Generated by Django 3.1.5 on 2021-02-03 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20210203_1922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cancelledorder',
            name='cancel_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]