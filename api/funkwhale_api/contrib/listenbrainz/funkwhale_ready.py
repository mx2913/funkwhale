import funkwhale_api
import liblistenbrainz

from config import plugins
from django.utils import timezone

from funkwhale_api.history import models as history_models
from funkwhale_api.favorites import models as favorites_models

from .funkwhale_startup import PLUGIN
from . import tasks


@plugins.register_hook(plugins.LISTENING_CREATED, PLUGIN)
def submit_listen(listening, conf, **kwargs):
    user_token = conf["user_token"]
    if not user_token and not conf["submit_listenings"]:
        return

    logger = PLUGIN["logger"]
    logger.info("Submitting listen to ListenBrainz")
    client = liblistenbrainz.ListenBrainz()
    client.set_auth_token(user_token)
    listen = get_lb_listen(listening)

    client.submit_single_listen(listen)


def get_lb_listen(listening):
    track = listening.track
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
        listened_at=listening.creation_date.timestamp(),
        release_name=release_name,
        additional_info=additional_info,
    )


@plugins.register_hook(plugins.FAVORITE_CREATED, PLUGIN)
def submit_favorite_creation(track_favorite, conf, **kwargs):
    user_token = conf["user_token"]
    if not user_token or not conf["submit_favorites"]:
        return
    logger = PLUGIN["logger"]
    logger.info("Submitting favorite to ListenBrainz")
    client = liblistenbrainz.ListenBrainz()
    track = track_favorite.track
    if not track.mbid:
        logger.warning(
            "This tracks doesn't have a mbid. Feedback will not be submited to Listenbrainz"
        )
        return
    client.submit_user_feedback(1, track.mbid)


@plugins.register_hook(plugins.FAVORITE_DELETED, PLUGIN)
def submit_favorite_deletion(track_favorite, conf, **kwargs):
    user_token = conf["user_token"]
    if not user_token or not conf["submit_favorites"]:
        return
    logger = PLUGIN["logger"]
    logger.info("Submitting favorite deletion to ListenBrainz")
    client = liblistenbrainz.ListenBrainz()
    track = track_favorite.track
    if not track.mbid:
        logger.warning(
            "This tracks doesn't have a mbid. Feedback will not be submited to Listenbrainz"
        )
        return
    client.submit_user_feedback(0, track.mbid)


@plugins.register_hook(plugins.LISTENING_SYNC, PLUGIN)
def sync_listenings_from_listenbrainz(user, conf):
    user_name = conf["user_name"]

    if not user_name or not conf["sync_listenings"]:
        return
    logger = PLUGIN["logger"]
    logger.info("Getting listenings from ListenBrainz")
    try:
        last_ts = (
            history_models.Listening.objects.filter(user=user)
            .filter(source="Listenbrainz")
            .latest("creation_date")
            .values_list("creation_date", flat=True)
        ).timestamp()
    except funkwhale_api.history.models.Listening.DoesNotExist:
        tasks.import_listenbrainz_listenings(user, user_name, 0)
        return

    tasks.import_listenbrainz_listenings(user, user_name, last_ts)


@plugins.register_hook(plugins.FAVORITE_SYNC, PLUGIN)
def sync_favorites_from_listenbrainz(user, conf):
    user_name = conf["user_name"]

    if not user_name or not conf["sync_favorites"]:
        return
    try:
        last_ts = (
            favorites_models.TrackFavorite.objects.filter(user=user)
            .filter(source="Listenbrainz")
            .latest("creation_date")
            .creation_date.timestamp()
        )
    except favorites_models.TrackFavorite.DoesNotExist:
        tasks.import_listenbrainz_favorites(user, user_name, 0)
        return

    tasks.import_listenbrainz_favorites(user, user_name, last_ts)
