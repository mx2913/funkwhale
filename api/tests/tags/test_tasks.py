from funkwhale_api.music import models as music_models
from funkwhale_api.tags import models, tasks


def test_get_tags_from_foreign_key(factories):
    rock_tag = factories["tags.Tag"](name="Rock")
    rap_tag = factories["tags.Tag"](name="Rap")
    artist = factories["music.Artist"]()
    factories["music.Track"].create_batch(3, artist=artist, set_tags=["rock", "rap"])
    factories["music.Track"].create_batch(
        3, artist=artist, set_tags=["rock", "rap", "techno"]
    )

    result = tasks.get_tags_from_foreign_key(
        ids=[artist.pk],
        foreign_key_model=music_models.Track,
        foreign_key_attr="artist",
    )

    assert result == {artist.pk: [rock_tag.pk, rap_tag.pk]}


def test_add_tags_batch(factories):
    rock_tag = factories["tags.Tag"](name="Rock")
    rap_tag = factories["tags.Tag"](name="Rap")
    factories["tags.Tag"]()
    artist = factories["music.Artist"]()

    data = {artist.pk: [rock_tag.pk, rap_tag.pk]}

    tasks.add_tags_batch(
        data,
        model=artist.__class__,
    )

    assert artist.get_tags() == ["Rap", "Rock"]


def test_update_musicbrainz_genre(factories, mocker):
    tag1 = factories["tags.Tag"](mbid="2628c282-9075-4736-b1f9-7012404d09e8")
    tag2 = factories["tags.Tag"](mbid=None)
    factories["tags.Tag"]()
    factories["tags.Tag"]()
    mb_genre = [
        {"name": "dnb", "id": "aaaac282-9075-4736-b1f9-7012404daaaa"},
        {"name": tag1.name, "id": "2628c282-9075-4736-b1f9-7012404d09e8"},
        {"name": tag2.name, "id": "2628c282-9075-4736-b1f9-7012404daaaa"},
    ]
    mocker.patch(
        "funkwhale_api.tags.tasks.fetch_musicbrainz_genre", return_value=mb_genre
    )
    tasks.update_musicbrainz_genre()

    assert (
        str(models.Tag.objects.get(name="dnb").mbid)
        == "aaaac282-9075-4736-b1f9-7012404daaaa"
    )
    assert (
        str(models.Tag.objects.get(name=tag2.name).mbid)
        == "2628c282-9075-4736-b1f9-7012404daaaa"
    )
    assert (
        str(models.Tag.objects.get(name=tag1.name).mbid)
        == "2628c282-9075-4736-b1f9-7012404d09e8"
    )


def test_sync_musicbrainz_tags(factories, mocker):
    objs = [
        factories["music.Artist"](mbid="2628c282-9075-4736-b1f9-7012404daaaa"),
        factories["music.Track"](mbid="2628c282-9075-4736-b1f9-7012404daaaa"),
        factories["music.Album"](mbid="2628c282-9075-4736-b1f9-7012404dacab"),
    ]
    obj_map = {"Artist": "artists", "Track": "recordings", "Album": "releases"}
    for obj in objs:
        obj_type = obj.__class__.__name__
        mocker.patch(
            f"funkwhale_api.tags.tasks.musicbrainz.api.{obj_map[obj_type]}.get",
            return_value={
                obj_map[obj_type][:-1]: {"tag-list": [{"name": "Amazing Tag"}]}
            },
        )

        tasks.sync_fw_item_tag_with_musicbrainz_tags(obj)
        obj.refresh_from_db()
        assert obj.tagged_items.all()[0].tag.name == "Amazing Tag"
