# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sceapp', '0002_auto_20150105_1149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='end_date',
            field=models.DateTimeField(default=b'0000-00-00 00:00:00', verbose_name=b'Fecha Salida', blank=True),
            preserve_default=True,
        ),
    ]
