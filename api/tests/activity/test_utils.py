from funkwhale_api.activity import utils


def test_get_activity(factories):
    user = factories["users.User"](with_actor=True)

    # to do : only support local activities update to suport federated activities
    activity_user = factories["users.User"](with_actor=True)
    listening = factories["history.Listening"](actor=activity_user.actor)
    favorite = factories["favorites.TrackFavorite"](actor=activity_user.actor)
    objects = list(utils.get_activity(user))
    assert objects == [favorite, listening]


def test_get_activity_honors_privacy_level(factories, anonymous_user):
    user = factories["users.User"]()
    user.create_actor(privacy_level="everyone")
    user2 = factories["users.User"]()
    user2.create_actor(privacy_level="instance")

    listening1 = factories["history.Listening"](actor=user.actor)
    favorite1 = factories["favorites.TrackFavorite"](actor=user.actor)

    factories["favorites.TrackFavorite"](actor=user2.actor)

    objects = list(utils.get_activity(anonymous_user))
    assert objects == [favorite1, listening1]
    # to do : test others
