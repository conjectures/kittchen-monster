# Generated by Django 3.1.3 on 2020-12-17 15:41

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20201211_2223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='cooking_time',
            field=models.PositiveIntegerField(default=10, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='post',
            name='servings',
            field=models.PositiveIntegerField(default=4, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]