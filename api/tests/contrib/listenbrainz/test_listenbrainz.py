import pytest
from django.urls import reverse
from config import plugins
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
