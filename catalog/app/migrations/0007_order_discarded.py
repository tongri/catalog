# Generated by Django 3.1.5 on 2021-02-03 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_product_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='discarded',
            field=models.BooleanField(default=False),
        ),
    ]
