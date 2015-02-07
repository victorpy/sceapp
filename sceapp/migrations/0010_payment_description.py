# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sceapp', '0009_configs'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='description',
            field=models.CharField(default=b'No desc', max_length=200),
            preserve_default=True,
        ),
    ]
