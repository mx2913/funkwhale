from django.urls import reverse

from funkwhale_api.activity import serializers, utils


def test_activity_view(factories, api_client, preferences, anonymous_user):
    preferences["common__api_authentication_required"] = False
    user = factories["users.User"](privacy_level="everyone")
    factories["favorites.TrackFavorite"](actor=user.actor)
    factories["history.Listening"]()
    url = reverse("api:v1:activity-list")
    objects = utils.get_activity(anonymous_user)
    serializer = serializers.AutoSerializer(objects, many=True)
    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data["results"] == serializer.data
