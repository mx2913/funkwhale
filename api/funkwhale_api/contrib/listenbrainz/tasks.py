import datetime
import pylistenbrainz

from config import plugins
from django.utils import timezone

from funkwhale_api.users import models
from funkwhale_api.taskapp import celery
from funkwhale_api.history import models as history_models
from funkwhale_api.music import models as music_models


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
        ):
            continue
        try:
            track = music_models.Track.objects.get(mbid=listen.recording_mbid)
        except music_models.Track.DoesNotExist:
            # to do : resolve non mbid listens ?
            continue

        user = user
        fw_listen = history_models.Listening(
            creation_date=listen.listened_at,
            track=track,
            user=user,
            from_listenbrainz=True,
        )
        fw_listens.append(fw_listen)

    history_models.Listening.objects.bulk_create(fw_listens)


@celery.app.task(name="listenbrainz.import_listenbrainz_favorites")
def import_listenbrainz_favorites():
    return "to do"
