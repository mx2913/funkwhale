# Generated by Django 4.2.9 on 2024-03-16 00:36

import django.contrib.postgres.search
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


def skip(apps, schema_editor):
    pass


def save_artist_credit(obj, ArtistCredit):
    artist_credit, created = ArtistCredit.objects.get_or_create(
        artist=obj.artist,
        joinphrase="",
        credit=obj.artist.name,
    )
    obj.artist_credit.set([artist_credit])
    obj.save()


def set_all_artists_credit(apps, schema_editor):
    Track = apps.get_model("music", "Track")
    Album = apps.get_model("music", "Album")
    ArtistCredit = apps.get_model("music", "ArtistCredit")

    for track in Track.objects.all():
        save_artist_credit(track, ArtistCredit)

    for album in Album.objects.all():
        save_artist_credit(album, ArtistCredit)


class Migration(migrations.Migration):
    dependencies = [
        ("music", "0057_auto_20221118_2108"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArtistCredit",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "fid",
                    models.URLField(
                        db_index=True, max_length=500, null=True, unique=True
                    ),
                ),
                (
                    "mbid",
                    models.UUIDField(blank=True, db_index=True, null=True, unique=True),
                ),
                (
                    "uuid",
                    models.UUIDField(db_index=True, default=uuid.uuid4, unique=True),
                ),
                (
                    "creation_date",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now
                    ),
                ),
                (
                    "body_text",
                    django.contrib.postgres.search.SearchVectorField(blank=True),
                ),
                ("credit", models.CharField(blank=True, max_length=500, null=True)),
                ("joinphrase", models.CharField(blank=True, max_length=250, null=True)),
                ("index", models.IntegerField(blank=True, null=True)),
                (
                    "artist",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="artist_credit",
                        to="music.artist",
                    ),
                ),
                (
                    "from_activity",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="federation.activity",
                    ),
                ),
            ],
            options={
                "ordering": ["index", "credit"],
            },
        ),
        migrations.AddField(
            model_name="album",
            name="artist_credit",
            field=models.ManyToManyField(
                related_name="albums",
                to="music.artistcredit",
            ),
        ),
        migrations.AddField(
            model_name="track",
            name="artist_credit",
            field=models.ManyToManyField(
                related_name="tracks",
                to="music.artistcredit",
            ),
        ),
        migrations.RunPython(set_all_artists_credit, skip),
        migrations.RemoveField(
            model_name="album",
            name="artist",
        ),
        migrations.RemoveField(
            model_name="track",
            name="artist",
        ),
    ]