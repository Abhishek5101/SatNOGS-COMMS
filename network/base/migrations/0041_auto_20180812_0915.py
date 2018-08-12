# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-08-12 09:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0040_auto_20180811_1350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='antenna',
            name='antenna_type',
            field=models.CharField(choices=[(b'dipole', b'Dipole'), (b'v-dipole', b'V-Dipole'), (b'yagi', b'Yagi'), (b'helical', b'Helical'), (b'parabolic', b'Parabolic'), (b'vertical', b'Verical'), (b'turnstile', b'Turnstile'), (b'quadrafilar', b'Quadrafilar'), (b'eggbeater', b'Eggbeater'), (b'lindenblad', b'Lindenblad'), (b'paralindy', b'Parasitic Lindenblad')], max_length=15),
        ),
    ]
