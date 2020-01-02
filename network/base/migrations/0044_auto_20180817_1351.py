# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-08-17 13:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0043_auto_20180817_0923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='antenna',
            name='antenna_type',
            field=models.CharField(choices=[('dipole', 'Dipole'), ('v-dipole', 'V-Dipole'), ('discone', 'Discone'), ('yagi', 'Yagi'), ('helical', 'Helical'), ('parabolic', 'Parabolic'), ('vertical', 'Verical'), ('turnstile', 'Turnstile'), ('quadrafilar', 'Quadrafilar'), ('eggbeater', 'Eggbeater'), ('lindenblad', 'Lindenblad'), ('paralindy', 'Parasitic Lindenblad')], max_length=15),
        ),
    ]
