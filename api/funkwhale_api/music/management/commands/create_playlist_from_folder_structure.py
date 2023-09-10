import os
import mutagen
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from funkwhale_api.music import models, utils
from funkwhale_api.playlists import models as playlist_models
from funkwhale_api.users import models as user_models


def create_or_check_playlist(self, playlist_name, user, **options):
    playlist = playlist_models.Playlist.objects.filter(
        Q(user=user) & Q(name=playlist_name)
    ).first()
    if not playlist:
        if options["yes"] is True:
            playlist = playlist_models.Playlist.objects.create(
                name=playlist_name, user=user, privacy_level=options["privacy_level"]
            )
            return playlist

        response = input(
            f"This playlist {playlist_name} will be created. Proceed? (y/n): "
        )
        if response.lower() == "y" or response.lower() == "yes":
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
            track = os.path.join(directory, file)
            try:
                audio = mutagen.File(track)
            except Exception:
                self.stdout.write(
                    f"Could not load {track} because of a mutagen exception"
                )
            if audio:
                mbid = (
                    audio.get("UFID:http://musicbrainz.org", None).data.decode()
                    if audio.get("UFID:http://musicbrainz.org", None)
                    else None
                )
                if not mbid:
                    self.stdout.write(f"Did not find mbid, skipping track {track}...")
                    continue

                try:
                    track_fw = models.Track.objects.get(mbid=mbid)
                except models.Track.DoesNotExist:
                    self.stdout.write(f"No track found for {track}")
                    continue

                if existing_tracks.filter(track__id=track_fw.id).exists():
                    self.stdout.write(f"Track already in playlist. Skipping {track}...")
                    continue

                fw_tracks.append(track_fw)

    return fw_tracks


def add_tracks_to_playlist(self, directory, playlist_name, user, **options):
    playlist = create_or_check_playlist(self, playlist_name, user, **options)
    fw_track_list = get_fw_track_list(self, directory, playlist, **options)

    if options["yes"] is True:
        return playlist.insert_many(fw_track_list, allow_duplicates=False)

    response = input(
        f"These tracks {fw_track_list} will be added to playlist {playlist_name}. Proceed? (y/n): "
    )
    if response.lower() == "y" or response.lower() == "yes":
        return playlist.insert_many(fw_track_list, allow_duplicates=False)


class Command(BaseCommand):
    help = """
    This command will create playlists based on a folder structure. It will use the base folder
    of each track as the playlist name. Subdirectories are taken into account but have independent
    playlists (tracks from subdirs will not appear in the base dir playlist). A confirmation is asked
    before playlist creation. Do not support duplicates in playlist. Only support mbid tagged files.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--user_id",
            help="User ID that will own the playlists",
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
            "--yes",
            action="store_true",
            help="Will create all playlists and add all tracks without confirmation",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        all_subdirectories = []

        for root, dirs, files in os.walk(options["dir_name"]):
            for dir_name in dirs:
                full_dir_path = os.path.join(root, dir_name)
                all_subdirectories.append(full_dir_path)
        user = user_models.User.objects.get(id=options["user_id"])

        for directory in all_subdirectories:
            self.stdout.write(f"Processing directory: {directory}")
            playlist_name = os.path.basename(directory)
            add_tracks_to_playlist(self, directory, playlist_name, user, **options)
