# Generated by Django 3.1.5 on 2021-02-02 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20210202_1223'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='price',
            field=models.PositiveSmallIntegerField(default=1000),
        ),
    ]