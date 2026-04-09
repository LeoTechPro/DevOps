# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('themes', '0003_auto_20160105_0809'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reference',
            old_name='model',
            new_name='theme',
        ),
        migrations.CreateModel(
            name='Blank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.CharField(max_length=1)),
                ('theme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='themes.Theme')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=1000)),
                ('time', models.DateTimeField(auto_now=True)),
                ('theme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='themes.Theme')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-time'],
            },
        ),
    ]
