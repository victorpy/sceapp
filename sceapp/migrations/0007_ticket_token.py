# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sceapp', '0006_auto_20150112_1426'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='token',
            field=models.CharField(default=b'No token', max_length=12),
            preserve_default=True,
        ),
    ]
