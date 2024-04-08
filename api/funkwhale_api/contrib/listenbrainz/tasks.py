import datetime

import liblistenbrainz
from django.utils import timezone

from config import plugins
from funkwhale_api.favorites import models as favorites_models
from funkwhale_api.history import models as history_models
from funkwhale_api.music import models as music_models
from funkwhale_api.taskapp import celery
from funkwhale_api.users import models

from .funkwhale_startup import PLUGIN


@celery.app.task(name="listenbrainz.trigger_listening_sync_with_listenbrainz")
def trigger_listening_sync_with_listenbrainz():
    now = timezone.now()
    active_month = now - datetime.timedelta(days=30)
    users = (
        models.User.objects.filter(plugins__code="listenbrainz")
        .filter(plugins__conf__sync_listenings=True)
        .filter(last_activity__gte=active_month)
    )
    for user in users:
        plugins.trigger_hook(
            plugins.LISTENING_SYNC,
            user=user,
            confs=plugins.get_confs(user),
        )


@celery.app.task(name="listenbrainz.trigger_favorite_sync_with_listenbrainz")
def trigger_favorite_sync_with_listenbrainz():
    now = timezone.now()
    active_month = now - datetime.timedelta(days=30)
    users = (
        models.User.objects.filter(plugins__code="listenbrainz")
        .filter(plugins__conf__sync_listenings=True)
        .filter(last_activity__gte=active_month)
    )
    for user in users:
        plugins.trigger_hook(
            plugins.FAVORITE_SYNC,
            user=user,
            confs=plugins.get_confs(user),
        )


@celery.app.task(name="listenbrainz.import_listenbrainz_listenings")
def import_listenbrainz_listenings(user, user_name, since):
    client = liblistenbrainz.ListenBrainz()
    response = client.get_listens(username=user_name, min_ts=since, count=100)
    listens = response["payload"]["listens"]
    while listens:
        add_lb_listenings_to_db(listens, user)
        new_ts = max(
            listens,
            key=lambda obj: datetime.datetime.fromtimestamp(
                obj.listened_at, timezone.utc
            ),
        )
        response = client.get_listens(username=user_name, min_ts=new_ts, count=100)
        listens = response["payload"]["listens"]


def add_lb_listenings_to_db(listens, user):
    logger = PLUGIN["logger"]
    fw_listens = []
    for listen in listens:
        if (
            listen.additional_info.get("submission_client")
            and listen.additional_info.get("submission_client")
            == "Funkwhale ListenBrainz plugin"
            and history_models.Listening.objects.filter(
                creation_date=datetime.datetime.fromtimestamp(
                    listen.listened_at, timezone.utc
                )
            ).exists()
        ):
            logger.info(
                f"Listen with ts {listen.listened_at} skipped because already in db"
            )
            continue

        mbid = (
            listen.mbid_mapping
            if hasattr(listen, "mbid_mapping")
            else listen.recording_mbid
        )

        if not mbid:
            logger.info("Received listening that doesn't have a mbid. Skipping...")

        try:
            track = music_models.Track.objects.get(mbid=mbid)
        except music_models.Track.DoesNotExist:
            logger.info(
                "Received listening that doesn't exist in fw database. Skipping..."
            )
            continue

        user = user
        fw_listen = history_models.Listening(
            creation_date=datetime.datetime.fromtimestamp(
                listen.listened_at, timezone.utc
            ),
            track=track,
            user=user,
            source="Listenbrainz",
        )
        fw_listens.append(fw_listen)

    history_models.Listening.objects.bulk_create(fw_listens)


@celery.app.task(name="listenbrainz.import_listenbrainz_favorites")
def import_listenbrainz_favorites(user, user_name, since):
    client = liblistenbrainz.ListenBrainz()
    response = client.get_user_feedback(username=user_name)
    offset = 0
    while response["feedback"]:
        count = response["count"]
        offset = offset + count
        last_sync = min(
            response["feedback"],
            key=lambda obj: datetime.datetime.fromtimestamp(
                obj["created"], timezone.utc
            ),
        )["created"]
        add_lb_feedback_to_db(response["feedback"], user)
        if last_sync <= since or count == 0:
            return
        response = client.get_user_feedback(username=user_name, offset=offset)


def add_lb_feedback_to_db(feedbacks, user):
    logger = PLUGIN["logger"]
    for feedback in feedbacks:
        try:
            track = music_models.Track.objects.get(mbid=feedback["recording_mbid"])
        except music_models.Track.DoesNotExist:
            logger.info(
                "Received feedback track that doesn't exist in fw database. Skipping..."
            )
            continue

        if feedback["score"] == 1:
            favorites_models.TrackFavorite.objects.get_or_create(
                user=user,
                creation_date=datetime.datetime.fromtimestamp(
                    feedback["created"], timezone.utc
                ),
                track=track,
                source="Listenbrainz",
            )
        elif feedback["score"] == 0:
            try:
                favorites_models.TrackFavorite.objects.get(
                    user=user, track=track
                ).delete()
            except favorites_models.TrackFavorite.DoesNotExist:
                continue
        elif feedback["score"] == -1:
            logger.info("Funkwhale doesn't support disliked tracks")
