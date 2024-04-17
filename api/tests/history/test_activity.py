from funkwhale_api.history import activities, serializers
from funkwhale_api.music.serializers import TrackActivitySerializer
from funkwhale_api.federation.serializers import APIActorSerializer


def test_get_listening_activity_url(settings, factories):
    user = factories["users.User"](with_actor=True)
    listening = factories["history.Listening"](actor=user.actor)
    user_url = listening.actor.user.get_activity_url()
    expected = f"{user_url}/listenings/tracks/{listening.pk}"
    assert listening.get_activity_url() == expected


def test_activity_listening_serializer(factories):
    listening = factories["history.Listening"]()

    actor = APIActorSerializer(listening.actor).data
    field = serializers.serializers.DateTimeField()
    expected = {
        "type": "Listen",
        "local_id": listening.pk,
        "id": listening.get_activity_url(),
        "actor": actor,
        "object": TrackActivitySerializer(listening.track).data,
        "published": field.to_representation(listening.creation_date),
    }

    data = serializers.ListeningActivitySerializer(listening).data

    assert data == expected


def test_track_listening_serializer_is_connected(activity_registry):
    conf = activity_registry["history.Listening"]
    assert conf["serializer"] == serializers.ListeningActivitySerializer


def test_track_listening_serializer_instance_activity_consumer(activity_registry):
    conf = activity_registry["history.Listening"]
    consumer = activities.broadcast_listening_to_instance_activity
    assert consumer in conf["consumers"]


def test_broadcast_listening_to_instance_activity(factories, mocker):
    p = mocker.patch("funkwhale_api.common.channels.group_send")
    user = factories["users.User"](with_actor=True)
    listening = factories["history.Listening"](actor=user.actor)
    data = serializers.ListeningActivitySerializer(listening).data
    consumer = activities.broadcast_listening_to_instance_activity
    message = {"type": "event.send", "text": "", "data": data}
    consumer(data=data, obj=listening)
    p.assert_called_once_with("instance_activity", message)


def test_broadcast_listening_to_instance_activity_private(factories, mocker):
    p = mocker.patch("funkwhale_api.common.channels.group_send")
    user = factories["users.User"](privacy_level="me", with_actor=True)
    listening = factories["history.Listening"](actor__user=user)
    data = serializers.ListeningActivitySerializer(listening).data
    consumer = activities.broadcast_listening_to_instance_activity
    consumer(data=data, obj=listening)
    p.assert_not_called()
