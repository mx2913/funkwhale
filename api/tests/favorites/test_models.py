import pytest

from funkwhale_api.favorites import models


@pytest.mark.parametrize(
    "privacy_level,expected",
    [("me", False), ("instance", True), ("everyone", True)],
)
def test_playable_by_local_actor(privacy_level, expected, factories):
    actor = factories["federation.Actor"](local=True)
    # default user actor is local
    user = factories["users.User"](with_actor=True, privacy_level=privacy_level)
    favorite = factories["favorites.TrackFavorite"](actor=user.actor)
    queryset = models.TrackFavorite.objects.all().viewable_by(actor)
    match = favorite in list(queryset)
    assert match is expected


@pytest.mark.parametrize(
    "privacy_level,expected", [("me", False), ("instance", False), ("everyone", True)]
)
def test_not_playable_by_remote_actor(privacy_level, expected, factories):
    actor = factories["federation.Actor"]()
    # default user actor is local
    user = factories["users.User"](
        with_actor=True,
        privacy_level=privacy_level,
    )
    favorite = factories["favorites.TrackFavorite"](actor=user.actor)
    queryset = models.TrackFavorite.objects.all().viewable_by(actor)
    match = favorite in list(queryset)
    assert match is expected
