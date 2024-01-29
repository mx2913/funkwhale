import os
import pytest

from funkwhale_api.music import filters, models

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def test_artist_filter_ordering(factories, mocker):
    # Lista de prueba
    artist1 = factories["music.Artist"](name="Anita Muller")
    artist2 = factories["music.Artist"](name="Jane Smith")
    artist3 = factories["music.Artist"](name="Adam Johnson")
    artist4 = factories["music.Artist"](name="anita iux")

    qs = models.Artist.objects.all()

    cf = factories["moderation.UserFilter"](for_artist=True)

    # Request con ordenamiento
    filterset = filters.ArtistFilter(
        {"ordering": "name"}, request=mocker.Mock(user=cf.user), queryset=qs
    )

    expected_order = [artist3.name, artist4.name, artist1.name, artist2.name]
    actual_order = list(filterset.qs.values_list("name", flat=True))

    assert actual_order == expected_order


def test_album_filter_hidden(factories, mocker, queryset_equal_list):
    factories["music.Album"]()
    cf = factories["moderation.UserFilter"](for_artist=True)

    hidden_album = factories["music.Album"](artist=cf.target_artist)

    qs = models.Album.objects.all()
    filterset = filters.AlbumFilter(
        {"hidden": "true"}, request=mocker.Mock(user=cf.user), queryset=qs
    )

    assert filterset.qs == [hidden_album]


def test_artist_filter_hidden(factories, mocker, queryset_equal_list):
    factories["music.Artist"]()
    cf = factories["moderation.UserFilter"](for_artist=True)
    hidden_artist = cf.target_artist

    qs = models.Artist.objects.all()
    filterset = filters.ArtistFilter(
        {"hidden": "true"}, request=mocker.Mock(user=cf.user), queryset=qs
    )

    assert filterset.qs == [hidden_artist]


def test_artist_filter_track_artist(factories, mocker, queryset_equal_list):
    factories["music.Track"]()
    cf = factories["moderation.UserFilter"](for_artist=True)
    hidden_track = factories["music.Track"](artist=cf.target_artist)

    qs = models.Track.objects.all()
    filterset = filters.TrackFilter(
        {"hidden": "true"}, request=mocker.Mock(user=cf.user), queryset=qs
    )

    assert filterset.qs == [hidden_track]


def test_artist_filter_track_album_artist(factories, mocker, queryset_equal_list):
    factories["music.Track"]()
    cf = factories["moderation.UserFilter"](for_artist=True)
    hidden_track = factories["music.Track"](album__artist=cf.target_artist)

    qs = models.Track.objects.all()
    filterset = filters.TrackFilter(
        {"hidden": "true"}, request=mocker.Mock(user=cf.user), queryset=qs
    )

    assert filterset.qs == [hidden_track]


@pytest.mark.parametrize(
    "factory_name, filterset_class",
    [
        ("music.Track", filters.TrackFilter),
        ("music.Artist", filters.ArtistFilter),
        ("music.Album", filters.AlbumFilter),
    ],
)
def test_track_filter_tag_single(
    factory_name,
    filterset_class,
    factories,
    mocker,
    queryset_equal_list,
    anonymous_user,
):
    factories[factory_name]()
    # tag name partially match the query, so this shouldn't match
    factories[factory_name](set_tags=["TestTag1"])
    tagged = factories[factory_name](set_tags=["TestTag"])
    qs = tagged.__class__.objects.all()
    filterset = filterset_class(
        {"tag": "testTaG"}, request=mocker.Mock(user=anonymous_user), queryset=qs
    )

    assert filterset.qs == [tagged]


@pytest.mark.parametrize(
    "factory_name, filterset_class",
    [
        ("music.Track", filters.TrackFilter),
        ("music.Artist", filters.ArtistFilter),
        ("music.Album", filters.AlbumFilter),
    ],
)
def test_track_filter_tag_multiple(
    factory_name,
    filterset_class,
    factories,
    mocker,
    queryset_equal_list,
    anonymous_user,
):
    factories[factory_name](set_tags=["TestTag1"])
    tagged = factories[factory_name](set_tags=["TestTag1", "TestTag2"])
    qs = tagged.__class__.objects.all()
    filterset = filterset_class(
        {"tag": ["testTaG1", "TestTag2"]},
        request=mocker.Mock(user=anonymous_user),
        queryset=qs,
    )

    assert filterset.qs == [tagged]


def test_channel_filter_track(factories, queryset_equal_list, mocker, anonymous_user):
    channel = factories["audio.Channel"](library__privacy_level="everyone")
    upload = factories["music.Upload"](
        library=channel.library, playable=True, track__artist=channel.artist
    )
    factories["music.Track"]()
    qs = upload.track.__class__.objects.all()
    filterset = filters.TrackFilter(
        {"channel": channel.uuid, "include_channels": "true"},
        request=mocker.Mock(user=anonymous_user, actor=None),
        queryset=qs,
    )

    assert filterset.qs == [upload.track]


def test_channel_filter_album(factories, queryset_equal_list, mocker, anonymous_user):
    channel = factories["audio.Channel"](library__privacy_level="everyone")
    upload = factories["music.Upload"](
        library=channel.library, playable=True, track__artist=channel.artist
    )
    factories["music.Album"]()
    qs = upload.track.album.__class__.objects.all()
    filterset = filters.AlbumFilter(
        {"channel": channel.uuid, "include_channels": "true"},
        request=mocker.Mock(user=anonymous_user, actor=None),
        queryset=qs,
    )

    assert filterset.qs == [upload.track.album]


def test_library_filter_track(factories, queryset_equal_list, mocker, anonymous_user):
    library = factories["music.Library"](privacy_level="everyone")
    upload = factories["music.Upload"](library=library, playable=True)
    factories["music.Track"]()
    qs = upload.track.__class__.objects.all()
    filterset = filters.TrackFilter(
        {"library": library.uuid},
        request=mocker.Mock(user=anonymous_user, actor=None),
        queryset=qs,
    )

    assert filterset.qs == [upload.track]


def test_library_filter_album(factories, queryset_equal_list, mocker, anonymous_user):
    library = factories["music.Library"](privacy_level="everyone")
    upload = factories["music.Upload"](library=library, playable=True)
    factories["music.Album"]()
    qs = upload.track.album.__class__.objects.all()
    filterset = filters.AlbumFilter(
        {"library": library.uuid},
        request=mocker.Mock(user=anonymous_user, actor=None),
        queryset=qs,
    )

    assert filterset.qs == [upload.track.album]


def test_library_filter_artist(factories, queryset_equal_list, mocker, anonymous_user):
    library = factories["music.Library"](privacy_level="everyone")
    upload = factories["music.Upload"](library=library, playable=True)
    factories["music.Artist"]()
    qs = upload.track.artist.__class__.objects.all()
    filterset = filters.ArtistFilter(
        {"library": library.uuid},
        request=mocker.Mock(user=anonymous_user, actor=None),
        queryset=qs,
    )

    assert filterset.qs == [upload.track.artist]


def test_track_filter_artist_includes_album_artist(
    factories, mocker, queryset_equal_list, anonymous_user
):
    factories["music.Track"]()
    track1 = factories["music.Track"]()
    track2 = factories["music.Track"](
        album__artist=track1.artist, artist=factories["music.Artist"]()
    )

    qs = models.Track.objects.all()
    filterset = filters.TrackFilter(
        {"artist": track1.artist.pk},
        request=mocker.Mock(user=anonymous_user),
        queryset=qs,
    )

    assert filterset.qs == [track2, track1]


@pytest.mark.parametrize(
    "factory_name, filterset_class",
    [
        ("music.Track", filters.TrackFilter),
        ("music.Artist", filters.ArtistFilter),
        ("music.Album", filters.AlbumFilter),
    ],
)
def test_filter_tag_related(
    factory_name,
    filterset_class,
    factories,
    anonymous_user,
    queryset_equal_list,
    mocker,
):
    factories["tags.Tag"](name="foo")
    factories["tags.Tag"](name="bar")
    factories["tags.Tag"](name="baz")
    factories["tags.Tag"]()
    factories["tags.Tag"]()

    matches = [
        factories[factory_name](set_tags=["foo", "bar", "baz", "noop"]),
        factories[factory_name](set_tags=["foo", "baz", "noop"]),
        factories[factory_name](set_tags=["baz", "noop"]),
    ]
    factories[factory_name](set_tags=["noop"]),
    obj = factories[factory_name](set_tags=["foo", "bar", "baz"])

    filterset = filterset_class(
        {"related": obj.pk, "ordering": "-related"},
        request=mocker.Mock(user=anonymous_user, actor=None),
        queryset=obj.__class__.objects.all(),
    )
    assert filterset.qs == matches


@pytest.mark.parametrize(
    "extension, mimetype", [("ogg", "audio/ogg"), ("mp3", "audio/mpeg")]
)
def test_track_filter_format(extension, mimetype, factories, mocker, anonymous_user):
    track_expected = factories["music.Track"]()
    name = ".".join(["test", extension])
    path = os.path.join(DATA_DIR, name)
    factories["music.Upload"](
        audio_file__from_path=path, track=track_expected, mimetype=mimetype
    )

    track_unexpected = factories["music.Track"]()
    path_wrong_ext = os.path.join(DATA_DIR, "test.m4a")
    factories["music.Upload"](
        audio_file__from_path=path_wrong_ext,
        track=track_unexpected,
        mimetype="audio/x-m4a",
    )

    qs = models.Track.objects.all()
    filterset = filters.TrackFilter(
        {"format": "ogg,mp3"},
        request=mocker.Mock(user=anonymous_user),
        queryset=qs,
    )

    assert filterset.qs[0] == track_expected


def test_album_filter_has_tags(factories, anonymous_user, mocker):
    album_expected = factories["music.Album"]()
    factories["music.Album"]()

    factories["tags.TaggedItem"](content_object=album_expected)

    qs = models.Album.objects.all()
    filterset = filters.AlbumFilter(
        {"has_tags": True},
        request=mocker.Mock(user=anonymous_user),
        queryset=qs,
    )

    assert filterset.qs[0] == album_expected


@pytest.mark.parametrize("fwobj", ["Album", "Track", "Artist"])
def test_filter_has_mbid(fwobj, factories, anonymous_user, mocker):
    obj_expected = factories[f"music.{fwobj}"](
        mbid="e9b9d574-537d-4d2d-a4c7-6f6c91eaf4e0"
    )

    factories[f"music.{fwobj}"](mbid=None)
    model_class = getattr(models, fwobj)
    qs = model_class.objects.all()

    filter_class = getattr(filters, f"{fwobj}Filter")
    filterset = filter_class(
        data={"has_mbid": True},
        request=mocker.Mock(user=anonymous_user),
        queryset=qs,
    )

    assert filterset.qs[0] == obj_expected


@pytest.mark.parametrize("quality", ["low", "medium", "high", "very_high"])
def test_track_quality_filter(factories, quality, mocker, anonymous_user):
    track_low = factories["music.Track"]()
    factories["music.Upload"](track=track_low, mimetype="audio/mp3", bitrate="20")

    track_low_aac = factories["music.Track"]()
    factories["music.Upload"](track=track_low_aac, mimetype="audio/x-m4a", bitrate="20")

    track_medium = factories["music.Track"]()
    factories["music.Upload"](track=track_medium, mimetype="audio/mp3", bitrate=194)

    qs = models.Track.objects.all()
    filterset = filters.TrackFilter(
        {"quality": quality},
        request=mocker.Mock(user=anonymous_user),
        queryset=qs,
    )

    if quality == "low":
        assert track_low in filterset.qs
        assert track_low_aac in filterset.qs

    if quality == "medium":
        assert filterset.qs[0] == track_medium

    if quality == "hight":
        assert filterset.qs[0] == track_medium


def test_album_has_cover(factories, mocker, anonymous_user):
    attachment_cover = factories["common.Attachment"]()
    album = factories["music.Album"](attachment_cover=attachment_cover)
    factories["music.Album"].create_batch(5)
    qs = models.Album.objects.all()
    filterset = filters.AlbumFilter(
        {"has_cover": True},
        request=mocker.Mock(user=anonymous_user),
        queryset=qs,
    )

    assert filterset.qs[0] == album


def test_album_has_release_date(factories, mocker, anonymous_user):
    album = factories["music.Album"]()
    factories["music.Album"](release_date=None)
    qs = models.Album.objects.all()
    filterset = filters.AlbumFilter(
        {"has_release_date": True},
        request=mocker.Mock(user=anonymous_user),
        queryset=qs,
    )

    assert filterset.qs[0] == album
