# Generated by Django 3.2.23 on 2024-01-11 14:34

import datetime
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("music", "0057_auto_20221118_2108"),
    ]

    operations = [
        migrations.CreateModel(
            name="UploadGroup",
            fields=[
                (
                    "name",
                    models.CharField(default=datetime.datetime.now, max_length=255),
                ),
                (
                    "guid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
            ],
        ),
    ]
