# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sceapp', '0005_auto_20150106_1634'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='created_by',
            field=models.CharField(default=b'None', max_length=64),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ticket',
            name='created_by',
            field=models.CharField(default=b'None', max_length=64),
            preserve_default=True,
        ),
    ]
