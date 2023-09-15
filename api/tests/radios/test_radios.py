import json
import logging
import random

import pytest
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.urls import reverse

from funkwhale_api.favorites.models import TrackFavorite
from funkwhale_api.music.models import Track
from funkwhale_api.radios import models, radios, serializers


def test_can_pick_track_from_choices():
    choices = [1, 2, 3, 4, 5]

    radio = radios.SimpleRadio()

    first_pick = radio.pick(choices=choices)

    assert first_pick in choices

    previous_choices = [first_pick]
    for remaining_choice in choices:
        pick = radio.pick(choices=choices, previous_choices=previous_choices)
        assert pick in set(choices).difference(set(previous_choices))


def test_can_pick_by_weight():
    choices_with_weight = [
        # choice, weight
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    ]

    picks = {choice: 0 for choice, weight in choices_with_weight}

    for i in range(1000):
        radio = radios.SimpleRadio()
        pick = radio.weighted_pick(choices=choices_with_weight)
        picks[pick] = picks[pick] + 1

    assert picks[5] > picks[4]
    assert picks[4] > picks[3]
    assert picks[3] > picks[2]
    assert picks[2] > picks[1]


def test_session_radio_excludes_previous_picks(factories):
    tracks = factories["music.Track"].create_batch(5)
    user = factories["users.User"]()
    previous_choices = []
    for i in range(5):
        TrackFavorite.add(track=random.choice(tracks), user=user)

    radio = radios.SessionRadio()
    radio.radio_type = "favorites"
    radio.start_session(user)

    for i in range(5):
        pick = radio.pick(user=user, filter_playable=False)
        assert pick in tracks
        assert pick not in previous_choices
        previous_choices.append(pick)

    with pytest.raises(ValueError):
        # no more picks available
        radio.pick(user=user, filter_playable=False)


def test_can_get_choices_for_favorites_radio(factories):
    files = factories["music.Upload"].create_batch(10)
    tracks = [f.track for f in files]
    user = factories["users.User"]()
    for i in range(5):
        TrackFavorite.add(track=random.choice(tracks), user=user)

    radio = radios.FavoritesRadio()
    choices = radio.get_choices(user=user)

    assert choices.count() == user.track_favorites.all().count()

    for favorite in user.track_favorites.all():
        assert favorite.track in choices

    for i in range(5):
        pick = radio.pick(user=user)
        assert pick in choices


def test_can_get_choices_for_custom_radio(factories):
    artist = factories["music.Artist"]()
    files = factories["music.Upload"].create_batch(5, track__artist=artist)
    tracks = [f.track for f in files]
    factories["music.Upload"].create_batch(5)

    session = factories["radios.CustomRadioSession"](
        custom_radio__config=[{"type": "artist", "ids": [artist.pk]}]
    )
    choices = session.radio.get_choices(filter_playable=False)

    expected = [t.pk for t in tracks]
    for t in list(choices.values_list("id", flat=True)):
        assert t in expected


def test_cannot_start_custom_radio_if_not_owner_or_not_public(factories):
    user = factories["users.User"]()
    artist = factories["music.Artist"]()
    radio = factories["radios.Radio"](config=[{"type": "artist", "ids": [artist.pk]}])
    serializer = serializers.RadioSessionSerializer(
        data={"radio_type": "custom", "custom_radio": radio.pk, "user": user.pk}
    )
    message = "You don't have access to this radio"
    assert not serializer.is_valid()
    assert message in serializer.errors["non_field_errors"]


def test_can_start_custom_radio_from_api(logged_in_api_client, factories):
    artist = factories["music.Artist"]()
    radio = factories["radios.Radio"](
        config=[{"type": "artist", "ids": [artist.pk]}], user=logged_in_api_client.user
    )
    url = reverse("api:v1:radios:sessions-list")
    response = logged_in_api_client.post(
        url, {"radio_type": "custom", "custom_radio": radio.pk}
    )
    assert response.status_code == 201
    session = radio.sessions.latest("id")
    assert session.radio_type == "custom"
    assert session.user == logged_in_api_client.user


def test_can_use_radio_session_to_filter_choices(factories):
    factories["music.Upload"].create_batch(10)
    user = factories["users.User"]()
    radio = radios.RandomRadio()
    session = radio.start_session(user)

    for i in range(10):
        radio.pick(filter_playable=False)

    # ensure 10 different tracks have been suggested
    tracks_id = [
        session_track.track.pk for session_track in session.session_tracks.all()
    ]
    assert len(set(tracks_id)) == 10


def test_can_restore_radio_from_previous_session(factories):
    user = factories["users.User"]()
    radio = radios.RandomRadio()
    session = radio.start_session(user)

    restarted_radio = radios.RandomRadio(session)
    assert radio.session == restarted_radio.session


def test_can_start_radio_for_logged_in_user(logged_in_api_client):
    url = reverse("api:v1:radios:sessions-list")
    logged_in_api_client.post(url, {"radio_type": "random"})
    session = models.RadioSession.objects.latest("id")
    assert session.radio_type == "random"
    assert session.user == logged_in_api_client.user


def test_can_get_track_for_session_from_api(factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    track = factories["music.Upload"](
        library__actor=actor, import_status="finished"
    ).track
    url = reverse("api:v1:radios:sessions-list")
    response = logged_in_api_client.post(url, {"radio_type": "random"})
    session = models.RadioSession.objects.latest("id")

    url = reverse("api:v1:radios:tracks-list")
    response = logged_in_api_client.post(url, {"session": session.pk})
    data = json.loads(response.content.decode("utf-8"))

    assert data["track"]["id"] == track.pk
    assert data["position"] == 1

    next_track = factories["music.Upload"](
        library__actor=actor, import_status="finished"
    ).track
    response = logged_in_api_client.post(url, {"session": session.pk})
    data = json.loads(response.content.decode("utf-8"))

    assert data["track"]["id"] == next_track.id
    assert data["position"] == 2


def test_can_get_track_for_session_from_api_v2(factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    track = factories["music.Upload"](
        library__actor=actor, import_status="finished"
    ).track
    url = reverse("api:v1:radios:sessions-list")
    response = logged_in_api_client.post(url, {"radio_type": "random"})
    session = models.RadioSession.objects.latest("id")

    url = reverse("api:v2:radios:tracks-list")
    response = logged_in_api_client.post(url, {"session": session.pk})
    data = json.loads(response.content.decode("utf-8"))

    assert data[0]["track"]["id"] == track.pk
    assert data[0]["position"] == 1

    next_track = factories["music.Upload"](
        library__actor=actor, import_status="finished"
    ).track
    response = logged_in_api_client.post(url, {"session": session.pk})
    data = json.loads(response.content.decode("utf-8"))

    assert data[0]["track"]["id"] == next_track.id
    assert data[0]["position"] == 2


def test_related_object_radio_validate_related_object(factories):
    user = factories["users.User"]()
    # cannot start without related object
    radio = radios.ArtistRadio()
    with pytest.raises(ValidationError):
        radio.start_session(user)

    # cannot start with bad related object type
    radio = radios.ArtistRadio()
    with pytest.raises(ValidationError):
        radio.start_session(user, related_object=user)


def test_can_start_artist_radio(factories):
    user = factories["users.User"]()
    artist = factories["music.Artist"]()
    factories["music.Upload"].create_batch(5)
    good_files = factories["music.Upload"].create_batch(5, track__artist=artist)
    good_tracks = [f.track for f in good_files]

    radio = radios.ArtistRadio()
    session = radio.start_session(user, related_object=artist)
    assert session.radio_type == "artist"
    for i in range(5):
        assert radio.pick(filter_playable=False) in good_tracks


def test_can_start_tag_radio(factories):
    user = factories["users.User"]()
    tag = factories["tags.Tag"]()
    good_tracks = [
        factories["music.Track"](set_tags=[tag.name]),
        factories["music.Track"](album__set_tags=[tag.name]),
        factories["music.Track"](album__artist__set_tags=[tag.name]),
    ]
    factories["music.Track"].create_batch(3, set_tags=["notrock"])

    radio = radios.TagRadio()
    session = radio.start_session(user, related_object=tag)
    assert session.radio_type == "tag"

    for i in range(3):
        assert radio.pick(filter_playable=False) in good_tracks


def test_can_start_actor_content_radio(factories):
    actor_library = factories["music.Library"](actor__local=True)
    good_tracks = [
        factories["music.Upload"](playable=True, library=actor_library).track,
        factories["music.Upload"](playable=True, library=actor_library).track,
        factories["music.Upload"](playable=True, library=actor_library).track,
    ]
    factories["music.Upload"].create_batch(3, playable=True)

    radio = radios.ActorContentRadio()
    session = radio.start_session(
        actor_library.actor.user, related_object=actor_library.actor
    )
    assert session.radio_type == "actor-content"

    for i in range(3):
        assert radio.pick() in good_tracks


def test_can_start_actor_content_radio_from_api(
    logged_in_api_client, preferences, factories
):
    actor = factories["federation.Actor"]()
    url = reverse("api:v1:radios:sessions-list")

    response = logged_in_api_client.post(
        url, {"radio_type": "actor-content", "related_object_id": actor.full_username}
    )

    assert response.status_code == 201

    session = models.RadioSession.objects.latest("id")

    assert session.radio_type == "actor-content"
    assert session.related_object == actor


def test_can_start_library_radio(factories):
    user = factories["users.User"]()
    library = factories["music.Library"]()
    good_tracks = [
        factories["music.Upload"](library=library).track,
        factories["music.Upload"](library=library).track,
        factories["music.Upload"](library=library).track,
    ]
    factories["music.Upload"].create_batch(3)

    radio = radios.LibraryRadio()
    session = radio.start_session(user, related_object=library)
    assert session.radio_type == "library"

    for i in range(3):
        assert radio.pick(filter_playable=False) in good_tracks


def test_can_start_library_radio_from_api(logged_in_api_client, preferences, factories):
    library = factories["music.Library"]()
    url = reverse("api:v1:radios:sessions-list")

    response = logged_in_api_client.post(
        url, {"radio_type": "library", "related_object_id": library.uuid}
    )

    assert response.status_code == 201

    session = models.RadioSession.objects.latest("id")

    assert session.radio_type == "library"
    assert session.related_object == library


def test_can_start_artist_radio_from_api(logged_in_api_client, preferences, factories):
    artist = factories["music.Artist"]()
    url = reverse("api:v1:radios:sessions-list")

    response = logged_in_api_client.post(
        url, {"radio_type": "artist", "related_object_id": artist.id}
    )

    assert response.status_code == 201

    session = models.RadioSession.objects.latest("id")

    assert session.radio_type == "artist"
    assert session.related_object == artist


def test_can_start_less_listened_radio(factories):
    user = factories["users.User"]()
    wrong_files = factories["music.Upload"].create_batch(5)
    for f in wrong_files:
        factories["history.Listening"](track=f.track, user=user)
    good_files = factories["music.Upload"].create_batch(5)
    good_tracks = [f.track for f in good_files]
    radio = radios.LessListenedRadio()
    radio.start_session(user)

    for i in range(5):
        assert radio.pick(filter_playable=False) in good_tracks


def test_similar_radio_track(factories):
    user = factories["users.User"]()
    seed = factories["music.Track"]()
    radio = radios.SimilarRadio()
    radio.start_session(user, related_object=seed)

    factories["music.Track"].create_batch(5)

    # one user listened to this track
    l1 = factories["history.Listening"](track=seed)

    expected_next = factories["music.Track"]()
    factories["history.Listening"](track=expected_next, user=l1.user)

    assert radio.pick(filter_playable=False) == expected_next


def test_session_radio_get_queryset_ignore_filtered_track_artist(
    factories, queryset_equal_list
):
    cf = factories["moderation.UserFilter"](for_artist=True)
    factories["music.Track"](artist=cf.target_artist)
    valid_track = factories["music.Track"]()
    radio = radios.RandomRadio()
    radio.start_session(user=cf.user)

    assert radio.get_queryset() == [valid_track]


def test_session_radio_get_queryset_ignore_filtered_track_album_artist(
    factories, queryset_equal_list
):
    cf = factories["moderation.UserFilter"](for_artist=True)
    factories["music.Track"](album__artist=cf.target_artist)
    valid_track = factories["music.Track"]()
    radio = radios.RandomRadio()
    radio.start_session(user=cf.user)

    assert radio.get_queryset() == [valid_track]


def test_get_choices_for_custom_radio_exclude_artist(factories):
    included_artist = factories["music.Artist"]()
    excluded_artist = factories["music.Artist"]()
    included_uploads = factories["music.Upload"].create_batch(
        5, track__artist=included_artist
    )
    factories["music.Upload"].create_batch(5, track__artist=excluded_artist)

    session = factories["radios.CustomRadioSession"](
        custom_radio__config=[
            {"type": "artist", "ids": [included_artist.pk]},
            {"type": "artist", "ids": [excluded_artist.pk], "not": True},
        ]
    )
    choices = session.radio.get_choices(filter_playable=False)

    expected = [u.track.pk for u in included_uploads]
    for t in list(choices.values_list("id", flat=True)):
        assert t in expected


def test_get_choices_for_custom_radio_exclude_tag(factories):
    included_uploads = factories["music.Upload"].create_batch(
        5, track__set_tags=["rap"]
    )
    factories["music.Upload"].create_batch(5, track__set_tags=["rock", "rap"])

    session = factories["radios.CustomRadioSession"](
        custom_radio__config=[
            {"type": "tag", "names": ["rap"]},
            {"type": "tag", "names": ["rock"], "not": True},
        ]
    )
    choices = session.radio.get_choices(filter_playable=False)

    expected = [u.track.pk for u in included_uploads]
    for t in list(choices.values_list("id", flat=True)):
        assert t in expected


def test_can_start_custom_multiple_radio_from_api(api_client, factories):
    tracks = factories["music.Track"].create_batch(5)
    url = reverse("api:v1:radios:sessions-list")
    map_filters_to_type = {"tags": "names", "artists": "ids", "playlists": "names"}
    for key, value in map_filters_to_type.items():
        attr = value[:-1]
        track_filter_key = [getattr(a.artist, attr) for a in tracks]
        config = {"filters": [{"type": key, value: track_filter_key}]}
        response = api_client.post(
            url,
            {"radio_type": "custom_multiple", "config": config},
            format="json",
        )
        assert response.status_code == 201


def test_session_radio_excludes_previous_picks_v2(factories, logged_in_api_client):
    tracks = factories["music.Track"].create_batch(5)
    url = reverse("api:v1:radios:sessions-list")
    response = logged_in_api_client.post(url, {"radio_type": "random"})
    session = models.RadioSession.objects.latest("id")
    url = reverse("api:v2:radios:tracks-list")

    previous_choices = []

    for i in range(5):
        response = logged_in_api_client.post(
            url, {"session": session.pk, "filter_playable": False}
        )
        pick = json.loads(response.content.decode("utf-8"))
        assert pick[0]["track"]["title"] not in previous_choices
        assert pick[0]["track"]["title"] in [t.title for t in tracks]
        previous_choices.append(pick[0]["track"]["title"])

    response = logged_in_api_client.post(url, {"session": session.pk})
    assert (
        json.loads(response.content.decode("utf-8"))
        == "Radio doesn't have more candidates"
    )


def test_can_get_choices_for_favorites_radio_v2(factories):
    files = factories["music.Upload"].create_batch(10)
    tracks = [f.track for f in files]
    user = factories["users.User"]()
    for i in range(5):
        TrackFavorite.add(track=random.choice(tracks), user=user)

    radio = radios.FavoritesRadio()
    session = radio.start_session(user=user)
    choices = session.radio.get_choices_v2(quantity=100, filter_playable=False)

    assert len(choices) == user.track_favorites.all().count()

    for favorite in user.track_favorites.all():
        assert favorite.track in choices


def test_can_get_choices_for_custom_radio_v2(factories):
    artist = factories["music.Artist"]()
    files = factories["music.Upload"].create_batch(5, track__artist=artist)
    tracks = [f.track for f in files]
    factories["music.Upload"].create_batch(5)

    session = factories["radios.CustomRadioSession"](
        custom_radio__config=[{"type": "artist", "ids": [artist.pk]}]
    )
    choices = session.radio.get_choices_v2(quantity=1, filter_playable=False)

    expected = [t.pk for t in tracks]
    for t in choices:
        assert t.id in expected


def test_can_cache_radio_track(factories):
    uploads = factories["music.Track"].create_batch(10)
    user = factories["users.User"]()
    radio = radios.RandomRadio()
    session = radio.start_session(user)
    picked = session.radio.pick_many_v2(quantity=1, filter_playable=False)
    assert len(picked) == 1
    for t in cache.get(f"radiosessiontracks{session.id}"):
        assert t.track in uploads


def test_regenerate_cache_if_not_enought_tracks_in_it(
    factories, caplog, logged_in_api_client
):
    logger = logging.getLogger("funkwhale_api.radios.radios")
    caplog.set_level(logging.INFO)
    logger.addHandler(caplog.handler)

    factories["music.Track"].create_batch(10)
    user = factories["users.User"]()
    url = reverse("api:v1:radios:sessions-list")
    response = logged_in_api_client.post(url, {"radio_type": "random"})
    session = models.RadioSession.objects.latest("id")
    url = reverse("api:v2:radios:tracks-list")
    logged_in_api_client.post(
        url, {"session": session.pk, "count": 9, "filter_playable": False}
    )
    response = logged_in_api_client.post(
        url, {"session": session.pk, "count": 10, "filter_playable": False}
    )
    pick = json.loads(response.content.decode("utf-8"))
    assert (
        "Not enough radio tracks in cache. Trying to generate new cache" in caplog.text
    )
    assert len(pick) == 1
