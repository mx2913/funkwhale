# Generated by Django 3.2.20 on 2023-11-29 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0002_auto_20180325_1433'),
    ]

    operations = [
        migrations.AddField(
            model_name='listening',
            name='from_listenbrainz',
            field=models.BooleanField(default=None, null=True),
        ),
    ]