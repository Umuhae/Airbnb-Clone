# Generated by Django 2.2.5 on 2020-12-14 19:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0004_auto_20201215_0405'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photo',
            name='name',
        ),
    ]
