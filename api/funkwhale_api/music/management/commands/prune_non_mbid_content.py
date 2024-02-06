from django.core.management.base import BaseCommand
from django.db import transaction

from funkwhale_api.music import models


class Command(BaseCommand):
    help = """Deletes any tracks not tagged with a MusicBrainz ID from the database. By default, any tracks that
        have been favorited by a user or added to a playlist are preserved."""

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-dry-run",
            action="store_true",
            dest="no_dry_run",
            default=True,
            help="Disable dry run mode and apply pruning for real on the database",
        )

        parser.add_argument(
            "--include-playlist-content",
            action="store_true",
            dest="include_playlist_content",
            default=False,
            help="Allow tracks included in playlists to be pruned",
        )

        parser.add_argument(
            "--include-favorites-content",
            action="store_true",
            dest="include_favorited_content",
            default=False,
            help="Allow favorited tracks to be pruned",
        )

        parser.add_argument(
            "--include-listened-content",
            action="store_true",
            dest="include_listened_content",
            default=False,
            help="Allow tracks with listening history to be pruned",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        tracks = models.Track.objects.filter(mbid__isnull=True)
        if not options["include_favorited_content"]:
            tracks = tracks.filter(track_favorites__isnull=True)
        if not options["include_playlist_content"]:
            tracks = tracks.filter(playlist_tracks__isnull=True)
        if not options["include_listened_content"]:
            tracks = tracks.filter(listenings__isnull=True)

        pruned_total = tracks.count()
        total = models.Track.objects.count()

        if options["no_dry_run"]:
            self.stdout.write(f"Deleting {pruned_total}/{total} tracks…")
            tracks.delete()
        else:
            self.stdout.write(f"Would prune {pruned_total}/{total} tracks")
