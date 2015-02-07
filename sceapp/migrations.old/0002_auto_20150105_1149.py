# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sceapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='end_date',
            field=models.DateTimeField(verbose_name=b'Fecha Salida', blank=True),
            preserve_default=True,
        ),
    ]
