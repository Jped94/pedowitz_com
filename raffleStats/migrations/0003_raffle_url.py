# Generated by Django 2.1.7 on 2019-03-01 04:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raffleStats', '0002_auto_20190217_2246'),
    ]

    operations = [
        migrations.AddField(
            model_name='raffle',
            name='url',
            field=models.TextField(default='poop'),
            preserve_default=False,
        ),
    ]
