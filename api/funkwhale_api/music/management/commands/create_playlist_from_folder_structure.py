import os

import mutagen
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from funkwhale_api.music import models, utils
from funkwhale_api.playlists import models as playlist_models
from funkwhale_api.users import models as user_models


def get_or_create_playlist(self, playlist_name, user, **options):
    playlist = playlist_models.Playlist.objects.filter(
        Q(user=user) & Q(name=playlist_name)
    ).first()
    if not playlist:
        if options["no_dry_run"]:
            playlist = playlist_models.Playlist.objects.create(
                name=playlist_name, user=user, privacy_level=options["privacy_level"]
            )
            return playlist

        response = input(
            f"This playlist {playlist_name} will be created. Proceed? (y/n): "
        )
        if response.lower() in "yes":
            playlist = playlist_models.Playlist.objects.create(
                name=playlist_name, user=user, privacy_level=options["privacy_level"]
            )
            return playlist
    else:
        return playlist


def get_fw_track_list(self, directory, playlist, **options):
    fw_tracks = []
    audio_extensions = utils.SUPPORTED_EXTENSIONS
    existing_tracks = playlist.playlist_tracks.select_for_update()
    for file in next(os.walk(directory))[2]:
        if file.endswith(tuple(audio_extensions)):
            track_path = os.path.join(directory, file)
            try:
                audio = mutagen.File(track_path)
            except mutagen.MutagenError as e:
                self.stdout.write(
                    f"Could not load {track_path} because of a mutagen exception : {e}"
                )
            if options["only_mbid"]:
                mbid = (
                    audio.get("UFID:http://musicbrainz.org", None).data.decode()
                    if audio.get("UFID:http://musicbrainz.org", None)
                    else None
                )
                if not mbid:
                    self.stdout.write(
                        f"Did not find mbid, skipping track {track_path}..."
                    )
                    continue

                try:
                    track_fw = models.Track.objects.get(mbid=mbid)
                except models.Track.DoesNotExist:
                    self.stdout.write(f"No track found for {track_path}")
                    continue

            else:
                try:
                    self.stdout.write(f"rack_path {str(track_path)}...")

                    track_fw = models.Upload.objects.get(source=track_path)
                except models.Upload.DoesNotExist:
                    self.stdout.write(f"No track found for {track_path}")
                    continue

            if existing_tracks.filter(track__id=track_fw.id).exists():
                self.stdout.write(
                    f"Track already in playlist. Skipping {track_path}..."
                )
                continue

            fw_tracks.append(track_fw)

    return fw_tracks


def add_tracks_to_playlist(self, directory, user, **options):
    playlist_name = os.path.basename(directory)
    playlist = get_or_create_playlist(self, playlist_name, user, **options)

    fw_track_list = get_fw_track_list(self, directory, playlist, **options)
    if options["no_dry_run"] is True:
        return playlist.insert_many(fw_track_list, allow_duplicates=False)

    response = input(
        f"These tracks {fw_track_list} will be added to playlist {playlist_name}. Proceed? (y/n): "
    )
    if response.lower() in "yes":
        return playlist.insert_many(fw_track_list, allow_duplicates=False)


class Command(BaseCommand):
    help = """
    This command creates playlists based on a folder structure. It uses the base folder
    of each track as the playlist name. Subdirectories are taken into account but generate independent
    playlists. Tracks contained in subdirectories don't appear in the parent directory playlist.
    You will be asked to confirm the action before the playlist is created. Duplicate content in the
    playlist isn't supported.

    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--user_name",
            help="User name that will own the playlists",
        )
        parser.add_argument(
            "--dir_name",
            help="Which directory to start from.",
        )
        parser.add_argument(
            "--privacy_level",
            default="me",
            choices=["me", "instance", "everyone"],
            help="Which privacy_level for the playlists.",
        )
        parser.add_argument(
            "--no_dry_run",
            default=False,
            help="Will actually write data into the database",
        )
        parser.add_argument(
            "--only_mbid",
            default=False,
            help='Only files tagged with mbid will be used. Can be useful to create playlist from folders \
            that are not "in-place" imported into funkwhale',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        all_subdirectories = []

        for root, dirs, files in os.walk(options["dir_name"]):
            for dir_name in dirs:
                full_dir_path = os.path.join(root, dir_name)
                all_subdirectories.append(full_dir_path)
        user = user_models.User.objects.get(username=options["user_name"])

        for directory in all_subdirectories:
            add_tracks_to_playlist(self, directory, user, **options)
