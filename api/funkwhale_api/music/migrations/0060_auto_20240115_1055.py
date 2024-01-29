# Generated by Django 3.2.23 on 2024-01-15 10:55

from django.db import migrations


def populate_upload_groups(apps, schema_editor):
    upload = apps.get_model("music", "Upload")
    upload_group = apps.get_model("music", "UploadGroup")
    for upload in upload.objects.all():
        group, _ = upload_group.objects.get_or_create(name=upload.import_reference)
        upload.upload_group = group
        upload.save()


class Migration(migrations.Migration):
    dependencies = [
        ("music", "0059_upload_upload_group"),
    ]

    operations = [migrations.RunPython(populate_upload_groups)]