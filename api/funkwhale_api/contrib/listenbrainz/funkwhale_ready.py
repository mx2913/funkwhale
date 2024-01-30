import liblistenbrainz
from django.utils import timezone

import funkwhale_api
from config import plugins

from .funkwhale_startup import PLUGIN


@plugins.register_hook(plugins.LISTENING_CREATED, PLUGIN)
def submit_listen(listening, conf, **kwargs):
    user_token = conf["user_token"]
    if not user_token:
        return

    logger = PLUGIN["logger"]
    logger.info("Submitting listen to ListenBrainz")
    client = liblistenbrainz.ListenBrainz()
    client.set_auth_token(user_token)
    listen = get_listen(listening.track)

    client.submit_single_listen(listen)


def get_listen(track):
    additional_info = {
        "media_player": "Funkwhale",
        "media_player_version": funkwhale_api.__version__,
        "submission_client": "Funkwhale ListenBrainz plugin",
        "submission_client_version": PLUGIN["version"],
        "tracknumber": track.position,
        "discnumber": track.disc_number,
    }

    if track.mbid:
        additional_info["recording_mbid"] = str(track.mbid)

    if track.album:
        if track.album.title:
            release_name = track.album.title
        if track.album.mbid:
            additional_info["release_mbid"] = str(track.album.mbid)

    if track.artist.mbid:
        additional_info["artist_mbids"] = [str(track.artist.mbid)]

    upload = track.uploads.filter(duration__gte=0).first()
    if upload:
        additional_info["duration"] = upload.duration

    return liblistenbrainz.Listen(
        track_name=track.title,
        artist_name=track.artist.name,
        listened_at=int(timezone.now()),
        release_name=release_name,
        additional_info=additional_info,
    )
