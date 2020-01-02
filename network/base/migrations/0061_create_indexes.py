# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2019-11-25 18:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0060_add_latest_tle_proxy_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='observation',
            name='end',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='observation',
            name='start',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='satellite',
            name='norad_cat_id',
            field=models.PositiveIntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='tle',
            name='tle0',
            field=models.CharField(blank=True, db_index=True, max_length=100),
        ),
        migrations.AddIndex(
            model_name='observation',
            index=models.Index(fields=['-start', '-end'], name='base_observ_start_bbb297_idx'),
        ),
        migrations.AddIndex(
            model_name='stationstatuslog',
            index=models.Index(fields=['-changed'], name='base_statio_changed_71df65_idx'),
        ),
        migrations.AddIndex(
            model_name='station',
            index=models.Index(fields=['-status', 'id'], name='base_statio_status_797b1c_idx'),
        ),
    ]
