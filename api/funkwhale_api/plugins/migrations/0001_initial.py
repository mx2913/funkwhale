# Generated by Django 2.2.4 on 2019-09-23 15:17

from django.conf import settings
import django.contrib.postgres.fields.jsonb
import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Plugin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=70, unique=True)),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_enabled', models.BooleanField()),
                ('config', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=None, encoder=django.core.serializers.json.DjangoJSONEncoder, max_length=50000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserPlugin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_enabled', models.BooleanField()),
                ('config', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=None, encoder=django.core.serializers.json.DjangoJSONEncoder, max_length=50000, null=True)),
                ('plugin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_plugins', to='plugins.Plugin')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_plugins', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'plugin')},
            },
        ),
    ]
