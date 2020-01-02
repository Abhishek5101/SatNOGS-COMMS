# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-09-15 15:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0048_auto_20180902_2217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='antenna',
            name='antenna_type',
            field=models.CharField(choices=[('dipole', 'Dipole'), ('v-dipole', 'V-Dipole'), ('discone', 'Discone'), ('ground', 'Ground Plane'), ('yagi', 'Yagi'), ('cross-yagi', b'Cross Yagi'), ('helical', 'Helical'), ('parabolic', 'Parabolic'), ('vertical', 'Verical'), ('turnstile', 'Turnstile'), ('quadrafilar', 'Quadrafilar'), ('eggbeater', 'Eggbeater'), ('lindenblad', 'Lindenblad'), ('paralindy', b'Parasitic Lindenblad')], max_length=15),
        ),
    ]
