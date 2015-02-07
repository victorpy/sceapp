# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('sceapp', '0002_auto_20150106_0933'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='start_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'Fecha Entrada'),
            preserve_default=True,
        ),
    ]
