# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('sceapp', '0003_auto_20150105_1208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='end_date',
            field=models.DateTimeField(null=True, verbose_name=b'Fecha Salida', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ticket',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Fecha Entrada'),
            preserve_default=True,
        ),
    ]
