# Generated by Django 4.2.9 on 2024-04-17 19:15

from django.db import migrations, models


def gen_privacy_level(apps, schema_editor):
    user_model = apps.get_model("users", "User")
    for user in user_model.objects.all():
        user.actor.privacy_level = user.actor.privacy_level
        user.actor.save(update_fields=["privacy_level"])


class Migration(migrations.Migration):
    dependencies = [
        ("federation", "0029_userfollow"),
    ]

    operations = [
        migrations.AddField(
            model_name="actor",
            name="privacy_level",
            field=models.CharField(
                choices=[
                    ("me", "Only me"),
                    ("followers", "Me and my followers"),
                    ("instance", "Everyone on my instance, and my followers"),
                    ("everyone", "Everyone, including people on other instances"),
                ],
                default="instance",
                max_length=30,
            ),
        ),
        migrations.RunPython(gen_privacy_level, reverse_code=migrations.RunPython.noop),
    ]
