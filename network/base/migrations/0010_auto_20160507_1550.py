# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-07 15:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_auto_20160506_0826'),
    ]

    operations = [
        migrations.CreateModel(
            name='DemodData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payload_demod', models.FileField(blank=True, null=True, upload_to='data_payloads')),
            ],
        ),
        migrations.RemoveField(
            model_name='data',
            name='payload_demode',
        ),
        migrations.AddField(
            model_name='demoddata',
            name='data',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='demoddata', to='base.Data'),
        ),
    ]
