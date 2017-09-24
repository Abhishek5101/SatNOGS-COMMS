# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-09 21:16
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0025_auto_20170909_2111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='observation',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='observations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='observation',
            name='ground_station',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='observations', to='base.Station'),
        ),
        migrations.AlterField(
            model_name='observation',
            name='satellite',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='observations', to='base.Satellite'),
        ),
        migrations.AlterField(
            model_name='observation',
            name='tle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='observations', to='base.Tle'),
        ),
        migrations.AlterField(
            model_name='observation',
            name='transmitter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='observations', to='base.Transmitter'),
        ),
        migrations.AlterField(
            model_name='observation',
            name='vetted_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='observations_vetted', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='station',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ground_stations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='station',
            name='rig',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ground_stations', to='base.Rig'),
        ),
        migrations.AlterField(
            model_name='tle',
            name='satellite',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tles', to='base.Satellite'),
        ),
        migrations.AlterField(
            model_name='transmitter',
            name='satellite',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transmitters', to='base.Satellite'),
        ),
    ]