# Generated by Django 2.2.16 on 2020-11-11 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20201111_1508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredienttable',
            name='unit',
            field=models.CharField(blank=True, choices=[('ml', 'ml'), ('L', 'L'), ('g', 'g'), ('cup', 'cup'), ('tsp', 'tsp'), ('tbsp', 'tbsp')], max_length=32),
        ),
    ]
