import datetime
import logging

import liblistenbrainz
import pytest
from django.urls import reverse
from django.utils import timezone

from config import plugins
from funkwhale_api.contrib.listenbrainz import funkwhale_ready
from funkwhale_api.favorites import models as favorites_models
from funkwhale_api.history import models as history_models


def test_listenbrainz_submit_listen(logged_in_client, mocker, factories):
    config = plugins.get_plugin_config(
        name="listenbrainz",
        description="A plugin that allows you to submit or sync your listens and favorites to ListenBrainz.",
        conf=[],
        source=False,
    )
    handler = mocker.Mock()
    plugins.register_hook(plugins.LISTENING_CREATED, config)(handler)
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
    logged_in_client.get(url)
    listening = history_models.Listening.objects.get(user=logged_in_client.user)
    handler.assert_called_once_with(listening=listening, conf=None)


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

    listens = {
        "payload": {
            "count": 25,
            "user_id": "-- the MusicBrainz ID of the user --",
            "listens": [
                liblistenbrainz.Listen(
                    track_name="test",
                    artist_name="artist_test",
                    recording_mbid="f89db7f8-4a1f-4228-a0a1-e7ba028b7476",
                    additional_info={"submission_client": "not funkwhale"},
                    listened_at=-3124224000,
                ),
                liblistenbrainz.Listen(
                    track_name="test2",
                    artist_name="artist_test2",
                    recording_mbid="54c60860-f43d-484e-b691-7ab7ec8de559",
                    additional_info={
                        "submission_client": "Funkwhale ListenBrainz plugin"
                    },
                    listened_at=1871,
                ),
                liblistenbrainz.Listen(
                    track_name="test3",
                    artist_name="artist_test3",
                    listened_at=0,
                ),
            ],
        }
    }
    no_more_listen = {
        "payload": {
            "count": 25,
            "user_id": "Bilbo",
            "listens": [],
        }
    }

    mocker.patch.object(
        funkwhale_ready.tasks.liblistenbrainz.ListenBrainz,
        "get_listens",
        side_effect=[listens, no_more_listen],
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
    # track lb fav
    factories["music.Track"](mbid="195565db-65f9-4d0d-b347-5f0c85509528")
    # random track
    factories["music.Track"]()
    # track lb neutral
    track = factories["music.Track"](mbid="c5af5351-dbbf-4481-b52e-a480b6c57986")
    favorite = factories["favorites.TrackFavorite"](track=track, user=user)
    # last_sync
    track_last_sync = factories["music.Track"](
        mbid="c878ef2f-c08d-4a81-a047-f2a9f978cec7"
    )
    factories["favorites.TrackFavorite"](track=track_last_sync, source="Listenbrainz")

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
                # last sync
                "created": 1690775094,
                "recording_mbid": "c878ef2f-c08d-4a81-a047-f2a9f978cec7",
                "score": -1,
                "user_id": user.username,
            },
            {
                "created": 1690775093,
                "recording_mbid": "1fd02cf2-7247-4715-8862-c378ec1965d2",
                "score": 1,
                "user_id": user.username,
            },
        ],
        "offset": 0,
        "total_count": 4,
    }
    empty_feedback = {"count": 0, "feedback": [], "offset": 0, "total_count": 0}
    mocker.patch.object(
        funkwhale_ready.tasks.liblistenbrainz.ListenBrainz,
        "get_user_feedback",
        side_effect=[feedbacks, empty_feedback],
    )

    funkwhale_ready.sync_favorites_from_listenbrainz(user, conf)

    assert favorites_models.TrackFavorite.objects.filter(
        track__mbid="195565db-65f9-4d0d-b347-5f0c85509528"
    ).exists()
    with pytest.raises(favorites_models.TrackFavorite.DoesNotExist):
        favorite.refresh_from_db()


def test_sync_favorites_from_listenbrainz_since(factories, mocker, caplog):
    logger = logging.getLogger("plugins")
    caplog.set_level(logging.INFO)
    logger.addHandler(caplog.handler)
    user = factories["users.User"]()
    # track lb fav
    factories["music.Track"](mbid="195565db-65f9-4d0d-b347-5f0c85509528")
    # track lb neutral
    track = factories["music.Track"](mbid="c5af5351-dbbf-4481-b52e-a480b6c57986")
    favorite = factories["favorites.TrackFavorite"](track=track, user=user)
    # track should be not synced
    factories["music.Track"](mbid="1fd02cf2-7247-4715-8862-c378ec196000")
    # last_sync
    track_last_sync = factories["music.Track"](
        mbid="c878ef2f-c08d-4a81-a047-f2a9f978cec7"
    )
    factories["favorites.TrackFavorite"](
        track=track_last_sync,
        user=user,
        source="Listenbrainz",
        creation_date=datetime.datetime.fromtimestamp(1690775094),
    )

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
                # last sync
                "created": 1690775094,
                "recording_mbid": "c878ef2f-c08d-4a81-a047-f2a9f978cec7",
                "score": -1,
                "user_id": user.username,
            },
            {
                "created": 1690775093,
                "recording_mbid": "1fd02cf2-7247-4715-8862-c378ec1965d2",
                "score": 1,
                "user_id": user.username,
            },
        ],
        "offset": 0,
        "total_count": 4,
    }
    second_feedback = {
        "count": 0,
        "feedback": [
            {
                "created": 0,
                "recording_mbid": "1fd02cf2-7247-4715-8862-c378ec196000",
                "score": 1,
                "user_id": user.username,
            },
        ],
        "offset": 0,
        "total_count": 0,
    }
    mocker.patch.object(
        funkwhale_ready.tasks.liblistenbrainz.ListenBrainz,
        "get_user_feedback",
        side_effect=[feedbacks, second_feedback],
    )

    funkwhale_ready.sync_favorites_from_listenbrainz(user, conf)

    assert favorites_models.TrackFavorite.objects.filter(
        track__mbid="195565db-65f9-4d0d-b347-5f0c85509528"
    ).exists()
    assert not favorites_models.TrackFavorite.objects.filter(
        track__mbid="1fd02cf2-7247-4715-8862-c378ec196000"
    ).exists()
    with pytest.raises(favorites_models.TrackFavorite.DoesNotExist):
        favorite.refresh_from_db()


def test_submit_favorites_to_listenbrainz(factories, mocker, caplog):
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
        "submit_favorites": True,
    }

    patch = mocker.patch.object(
        funkwhale_ready.tasks.liblistenbrainz.ListenBrainz,
        "submit_user_feedback",
        return_value="Success",
    )
    funkwhale_ready.submit_favorite_creation(favorite, conf)

    patch.assert_called_once_with(1, track.mbid)


def test_submit_favorites_deletion(factories, mocker, caplog):
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
        "submit_favorites": True,
    }

    patch = mocker.patch.object(
        funkwhale_ready.tasks.liblistenbrainz.ListenBrainz,
        "submit_user_feedback",
        return_value="Success",
    )
    funkwhale_ready.submit_favorite_deletion(favorite, conf)

    patch.assert_called_once_with(0, track.mbid)
