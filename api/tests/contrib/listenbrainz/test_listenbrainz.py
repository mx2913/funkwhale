import datetime
import logging

import pytest
import pylistenbrainz

from django.urls import reverse
from django.utils import timezone

from config import plugins
from funkwhale_api.contrib.listenbrainz import funkwhale_ready
from funkwhale_api.favorites import models as favorites_models
from funkwhale_api.history import models as history_models


def test_listenbrainz_submit_listen(logged_in_client, mocker, factories):
    plugin = plugins.get_plugin_config(
        name="listenbrainz",
        description="A plugin that allows you to submit or sync your listens and favorites to ListenBrainz.",
        conf=[],
        source=False,
    )
    handler = mocker.Mock()
    plugins.register_hook(plugins.LISTENING_CREATED, plugin)(handler)
    plugins.set_conf(
        "listenbrainz",
        {
            "sync_listenings": True,
            "sync_facorites": True,
            "submit_favorites": True,
            "sync_favorites": True,
            "user_token": "blablabla",
        },
        user=logged_in_client.user,
    )
    plugins.enable_conf("listenbrainz", True, logged_in_client.user)

    track = factories["music.Track"]()
    url = reverse("api:v1:history:listenings-list")
    logged_in_client.post(url, {"track": track.pk})
    response = logged_in_client.get(url)
    listening = history_models.Listening.objects.get(user=logged_in_client.user)
    handler.assert_called_once_with(listening=listening, conf=None)
    # why conf=none ?


def test_sync_listenings_from_listenbrainz(factories, mocker, caplog):
    logger = logging.getLogger("plugins")
    caplog.set_level(logging.INFO)
    logger.addHandler(caplog.handler)
    user = factories["users.User"]()

    factories["music.Track"](mbid="f89db7f8-4a1f-4228-a0a1-e7ba028b7476")
    track = factories["music.Track"](mbid="54c60860-f43d-484e-b691-7ab7ec8de559")
    factories["history.Listening"](
        creation_date=datetime.datetime.fromtimestamp(1871, timezone.utc), track=track
    )

    conf = {
        "user_name": user.username,
        "user_token": "user_tolkien",
        "sync_listenings": True,
    }

    listens = [
        pylistenbrainz.Listen(
            track_name="test",
            artist_name="artist_test",
            recording_mbid="f89db7f8-4a1f-4228-a0a1-e7ba028b7476",
            additional_info={"submission_client": "not funkwhale"},
            listened_at=-3124224000,
        ),
        pylistenbrainz.Listen(
            track_name="test2",
            artist_name="artist_test2",
            recording_mbid="54c60860-f43d-484e-b691-7ab7ec8de559",
            additional_info={"submission_client": "Funkwhale ListenBrainz plugin"},
            listened_at=1871,
        ),
        pylistenbrainz.Listen(
            track_name="test3",
            artist_name="artist_test3",
            listened_at=0,
        ),
    ]

    mocker.patch.object(
        funkwhale_ready.tasks.pylistenbrainz.ListenBrainz,
        "get_listens",
        return_value=listens,
    )

    funkwhale_ready.sync_listenings_from_listenbrainz(user, conf)

    assert history_models.Listening.objects.filter(
        track__mbid="f89db7f8-4a1f-4228-a0a1-e7ba028b7476"
    ).exists()

    assert "Listen with ts 1871 skipped because already in db" in caplog.text
    assert "Received listening doesn't have a mbid" in caplog.text


def test_sync_favorites_from_listenbrainz(factories, mocker, caplog):
    logger = logging.getLogger("plugins")
    caplog.set_level(logging.INFO)
    logger.addHandler(caplog.handler)
    user = factories["users.User"]()

    factories["music.Track"](mbid="195565db-65f9-4d0d-b347-5f0c85509528")

    factories["music.Track"](mbid="54c60860-f43d-484e-b691-7ab7ec8de559")
    track = factories["music.Track"](mbid="c5af5351-dbbf-4481-b52e-a480b6c57986")

    favorite = factories["favorites.TrackFavorite"](track=track)

    conf = {
        "user_name": user.username,
        "user_token": "user_tolkien",
        "sync_favorites": True,
    }

    feedbacks = {
        "count": 5,
        "feedback": [
            {
                "created": 1701116226,
                "recording_mbid": "195565db-65f9-4d0d-b347-5f0c85509528",
                "score": 1,
                "user_id": user.username,
            },
            {
                "created": 1701116214,
                "recording_mbid": "c5af5351-dbbf-4481-b52e-a480b6c57986",
                "score": 0,
                "user_id": user.username,
            },
            {
                "created": 1690775094,
                "recording_mbid": "c878ef2f-c08d-4a81-a047-f2a9f978cec7",
                "score": -1,
                "user_id": user.username,
            },
            {
                "created": 1690775093,
                "recording_mbid": "1fd02cf2-7247-4715-8862-c378ec1965d2 ",
                "score": 1,
                "user_id": user.username,
            },
        ],
        "offset": 0,
        "total_count": 4,
    }
    mocker.patch.object(
        funkwhale_ready.tasks.pylistenbrainz.ListenBrainz,
        "get_user_feedback",
        return_value=feedbacks,
    )

    funkwhale_ready.sync_favorites_from_listenbrainz(user, conf)

    assert favorites_models.TrackFavorite.objects.filter(
        track__mbid="195565db-65f9-4d0d-b347-5f0c85509528"
    ).exists()
    with pytest.raises(deleted.DoesNotExist):
        favorite.refresh_from_db()
