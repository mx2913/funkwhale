import datetime
import pylistenbrainz

from django.utils import timezone
from config import plugins
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
def import_listenbrainz_listenings(user, user_name, ts):
    client = pylistenbrainz.ListenBrainz()
    listens = client.get_listens(username=user_name, min_ts=ts, count=100)
    add_lb_listenings_to_db(listens, user)
    new_ts = 13
    last_ts = 12
    while new_ts != last_ts:
        last_ts = listens[0].listened_at
        listens = client.get_listens(username=user_name, min_ts=new_ts, count=100)
        new_ts = listens[0].listened_at
        add_lb_listenings_to_db(listens, user)


def add_lb_listenings_to_db(listens, user):
    fw_listens = []
    for listen in listens:
        if (
            listen.additional_info.get("submission_client")
            and listen.additional_info.get("submission_client")
            == "Funkwhale ListenBrainz plugin"
            and history_models.Listening.objects.filter(
                creation_date=listen.listened_at
            ).exists()
        ):
            continue

        mbid = (
            listen.mbid_mapping
            if hasattr(listen, "mbid_mapping")
            else listen.recording_mbid
        )

        if not mbid:
            logger = PLUGIN["logger"]
            logger.info("Received listening doesn't have a mbid. Skipping...")

        try:
            track = music_models.Track.objects.get(mbid=mbid)
        except music_models.Track.DoesNotExist:
            logger.info("Received listening doesn't exist in fw database. Skipping...")
            continue

        user = user
        fw_listen = history_models.Listening(
            creation_date=timezone.make_aware(listen.listened_at),
            track=track,
            user=user,
            source="Listenbrainz",
        )
        fw_listens.append(fw_listen)

    history_models.Listening.objects.bulk_create(fw_listens)


@celery.app.task(name="listenbrainz.import_listenbrainz_favorites")
def import_listenbrainz_favorites():
    return "to do"
