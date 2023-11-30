import datetime

import pylistenbrainz
import pytest

from funkwhale_api.contrib.listenbrainz import tasks
from funkwhale_api.history import models as history_models


def test_import_listenbrainz_listenings(factories, mocker):
    factories["music.Track"](mbid="f89db7f8-4a1f-4228-a0a1-e7ba028b7476")
    factories["music.Track"](mbid="54c60860-f43d-484e-b691-7ab7ec8de559")

    listens = [
        pylistenbrainz.utils.Listen(
            track_name="test",
            artist_name="artist_test",
            recording_mbid="f89db7f8-4a1f-4228-a0a1-e7ba028b7476",
            additional_info={"submission_client": "not funkwhale"},
            listened_at=datetime.datetime.fromtimestamp(-3124224000),
        ),
        pylistenbrainz.utils.Listen(
            track_name="test2",
            artist_name="artist_test2",
            recording_mbid="54c60860-f43d-484e-b691-7ab7ec8de559",
            additional_info={"submission_client": "Funkwhale ListenBrainz plugin"},
            listened_at=datetime.datetime.fromtimestamp(1871),
        ),
        pylistenbrainz.utils.Listen(
            track_name="test3",
            artist_name="artist_test3",
            listened_at=0,
        ),
    ]

    mocker.patch.object(
        tasks.pylistenbrainz.ListenBrainz, "get_listens", return_value=listens
    )
    user = factories["users.User"]()

    tasks.import_listenbrainz_listenings(user, "user_name", ts=0)

    history_models.Listening.objects.filter(
        track__mbid="f89db7f8-4a1f-4228-a0a1-e7ba028b7476"
    ).exists()

    assert not history_models.Listening.objects.filter(
        track__mbid="54c60860-f43d-484e-b691-7ab7ec8de559"
    ).exists()
