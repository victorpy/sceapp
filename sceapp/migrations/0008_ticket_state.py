# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sceapp', '0007_ticket_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='state',
            field=models.CharField(default=b'A', max_length=1),
            preserve_default=True,
        ),
    ]
