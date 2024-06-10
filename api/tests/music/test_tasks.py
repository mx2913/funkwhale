import datetime
import os
import uuid

import pytest
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from funkwhale_api.common import utils as common_utils
from funkwhale_api.federation import jsonld
from funkwhale_api.federation import serializers as federation_serializers
from funkwhale_api.federation import utils as federation_utils
from funkwhale_api.music import licenses, metadata, models, signals, tasks

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


# DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")


def test_can_create_track_from_file_metadata_no_mbid(db, mocker):
    add_tags = mocker.patch("funkwhale_api.tags.models.add_tags")
    metadata = {
        "title": "Test track",
        "artist_credit": [{"credit": "Test artist", "joinphrase": ""}],
        "album": {"title": "Test album", "release_date": datetime.date(2012, 8, 15)},
        "position": 4,
        "disc_number": 2,
        "license": "Hello world: http://creativecommons.org/licenses/by-sa/4.0/",
        "copyright": "2018 Someone",
        "tags": ["Punk", "Rock"],
    }
    match_license = mocker.spy(licenses, "match")

    track = tasks.get_track_from_import_metadata(metadata)

    assert track.title == metadata["title"]
    assert track.mbid is None
    assert track.position == 4
    assert track.disc_number == 2
    assert track.license.code == "cc-by-sa-4.0"
    assert track.copyright == metadata["copyright"]
    assert track.album.title == metadata["album"]["title"]
    assert track.album.mbid is None
    assert track.album.release_date == datetime.date(2012, 8, 15)
    assert (
        track.artist_credit.all()[0].artist.name
        == metadata["artist_credit"][0]["credit"]
    )
    assert track.artist_credit.all()[0].artist.mbid is None
    assert track.artist_credit.all()[0].artist.attributed_to is None
    match_license.assert_called_once_with(metadata["license"], metadata["copyright"])
    add_tags.assert_any_call(track, *metadata["tags"])
    add_tags.assert_any_call(track.artist_credit.all()[0].artist, *[])
    add_tags.assert_any_call(track.album, *[])


def test_can_create_track_from_file_metadata_attributed_to(factories, mocker):
    actor = factories["federation.Actor"]()
    metadata = {
        "title": "Test track",
        "artist_credit": [{"credit": "Test artist", "joinphrase": ""}],
        "album": {"title": "Test album", "release_date": datetime.date(2012, 8, 15)},
        "position": 4,
        "disc_number": 2,
        "copyright": "2018 Someone",
    }

    track = tasks.get_track_from_import_metadata(metadata, attributed_to=actor)

    assert track.title == metadata["title"]
    assert track.mbid is None
    assert track.position == 4
    assert track.disc_number == 2
    assert track.copyright == metadata["copyright"]
    assert track.attributed_to == actor
    assert track.album.title == metadata["album"]["title"]
    assert track.album.mbid is None
    assert track.album.release_date == datetime.date(2012, 8, 15)
    assert track.album.attributed_to == actor
    assert (
        track.artist_credit.all()[0].artist.name
        == metadata["artist_credit"][0]["credit"]
    )
    assert track.artist_credit.all()[0].artist.mbid is None
    assert track.artist_credit.all()[0].artist.attributed_to == actor


def test_can_create_track_from_file_metadata_featuring(mocker):
    metadata = {
        "title": "Whole Lotta Love",
        "position": 1,
        "disc_number": 1,
        "mbid": "508704c0-81d4-4c94-ba58-3fc0b7da23eb",
        "album": {
            "title": "Guitar Heaven: The Greatest Guitar Classics of All Time",
            "mbid": "d06f2072-4148-488d-af6f-69ab6539ddb8",
            "release_date": datetime.date(2010, 9, 17),
            "artist_credit": [
                {
                    "credit": "Santana",
                    "mbid": "9a3bf45c-347d-4630-894d-7cf3e8e0b632",
                    "joinphrase": "",
                }
            ],
        },
        "artist_credit": [
            {"credit": "Santana feat Chris Cornell", "mbid": None, "joinphrase": ""}
        ],
    }
    mb_ac = {
        "artist-credit": [
            {
                "joinphrase": " feat ",
                "artist": {
                    "id": "9a3bf45c-347d-4630-894d-7cf3e8e0b632",
                    "type": "Group",
                    "name": "Santana",
                    "sort-name": "Santana",
                },
            },
            {
                "artist": {
                    "id": "11e46b16-2f25-4783-ab32-25250befe84a",
                    "type": "Person",
                    "name": "Chris Cornell",
                    "sort-name": "Chris Cornell",
                },
                "joinphrase": "",
            },
        ]
    }
    mb_ac_album = {
        "artist-credit": [
            {
                "artist": {
                    "id": "9a3bf45c-347d-4630-894d-7cf3e8e0b632",
                    "type": "Group",
                    "name": "Santana",
                    "sort-name": "Santana",
                }
            },
        ]
    }
    mocker.patch.object(
        tasks.musicbrainz.api.recordings, "get", return_value={"recording": mb_ac}
    )
    mocker.patch.object(
        tasks.musicbrainz.api.releases, "get", return_value={"recording": mb_ac_album}
    )
    track = tasks.get_track_from_import_metadata(metadata)

    assert track.album.artist_credit.all()[0].artist.name == "Santana"
    assert track.get_artist_credit_string == "Santana feat Chris Cornell"


def test_can_create_track_from_file_metadata_description(factories):
    metadata = {
        "title": "Whole Lotta Love",
        "position": 1,
        "disc_number": 1,
        "description": {"text": "hello there", "content_type": "text/plain"},
        "album": {"title": "Test album"},
        "artist_credit": [{"credit": "Santana", "joinphrase": ""}],
    }
    track = tasks.get_track_from_import_metadata(metadata)

    assert track.description.text == "hello there"
    assert track.description.content_type == "text/plain"


def test_can_create_track_from_file_metadata_use_featuring(factories):
    metadata = {
        "title": "Whole Lotta Love",
        "position": 1,
        "disc_number": 1,
        "description": {"text": "hello there", "content_type": "text/plain"},
        "album": {"title": "Test album"},
        "artist_credit": [
            {"credit": "Santana", "joinphrase": ", ", "index": 0},
            {"credit": "Anatnas", "joinphrase": "", "index": 1},
        ],
    }
    track = tasks.get_track_from_import_metadata(metadata)
    assert track.get_artist_credit_string == "Santana, Anatnas"


def test_can_create_track_from_file_metadata_mbid(factories, mocker):
    metadata = {
        "title": "Test track",
        "artist_credit": [
            {
                "credit": "Test artist",
                "mbid": "9c6bddde-6228-4d9f-ad0d-03f6fcb19e13",
                "joinphrase": "",
            }
        ],
        "album": {
            "title": "Test album",
            "release_date": datetime.date(2012, 8, 15),
            "mbid": "9c6bddde-6478-4d9f-ad0d-03f6fcb19e15",
            "artist_credit": [
                {
                    "credit": "Test album artist",
                    "mbid": "9c6bddde-6478-4d9f-ad0d-03f6fcb19e13",
                    "joinphrase": "",
                }
            ],
        },
        "position": 4,
        "mbid": "f269d497-1cc0-4ae4-a0c4-157ec7d73fcb",
        "cover_data": {"content": b"image_content", "mimetype": "image/png"},
    }
    mb_ac = {
        "artist-credit": [
            {
                "artist": {
                    "id": "9c6bddde-6228-4d9f-ad0d-03f6fcb19e13",
                    "name": "Test artist",
                },
                "joinphrase": "",
                "name": "Test artist",
            }
        ]
    }
    mb_ac_album = {
        "artist-credit": [
            {
                "artist": {
                    "id": "9c6bddde-6478-4d9f-ad0d-03f6fcb19e13",
                    "name": "Test album artist",
                },
                "name": "s",
            },
            "; ",
        ]
    }

    mocker.patch.object(
        tasks.musicbrainz.api.recordings, "get", return_value={"recording": mb_ac}
    )
    mocker.patch.object(
        tasks.musicbrainz.api.releases, "get", return_value={"recording": mb_ac_album}
    )

    track = tasks.get_track_from_import_metadata(metadata)

    assert track.title == metadata["title"]
    assert track.mbid == metadata["mbid"]
    assert track.position == 4
    assert track.disc_number is None
    assert track.album.title == metadata["album"]["title"]
    assert track.album.mbid == metadata["album"]["mbid"]
    assert (
        str(track.album.artist_credit.all()[0].artist.mbid)
        == metadata["album"]["artist_credit"][0]["mbid"]
    )
    assert (
        track.album.artist_credit.all()[0].artist.name
        == metadata["album"]["artist_credit"][0]["credit"]
    )
    assert track.album.release_date == datetime.date(2012, 8, 15)
    assert (
        track.artist_credit.all()[0].artist.name
        == metadata["artist_credit"][0]["credit"]
    )
    assert (
        str(track.artist_credit.all()[0].artist.mbid)
        == metadata["artist_credit"][0]["mbid"]
    )


def test_can_create_track_from_file_metadata_mbid_existing_album_artist(
    factories, mocker
):
    artist_credit = factories["music.ArtistCredit"](joinphrase="", index=0)
    album = factories["music.Album"](artist_credit=artist_credit)
    metadata = {
        "album": {
            "mbid": album.mbid,
            "title": "",
            "artist_credit": [
                {
                    "credit": "",
                    "joinphrase": "",
                    "mbid": album.artist_credit.all()[0].mbid,
                }
            ],
        },
        "title": "Hello",
        "position": 4,
        "artist_credit": [
            {"mbid": album.artist_credit.all()[0].mbid, "credit": "", "joinphrase": ""}
        ],
        "mbid": "f269d497-1cc0-4ae4-a0c4-157ec7d73acb",
    }
    mb_ac_album = {
        "artist-credit": [
            {
                "artist": {
                    "id": artist_credit.artist.mbid,
                    "name": artist_credit.artist.name,
                },
                "name": artist_credit.artist.name,
            },
            "; ",
        ]
    }
    mb_ac = {
        "artist-credit": [
            {
                "artist": {
                    "id": album.artist_credit.all()[0].artist.mbid,
                    "name": "Test artist",
                },
                "joinphrase": "",
                "name": album.artist_credit.all()[0].artist.name,
            }
        ]
    }

    mocker.patch.object(
        tasks.musicbrainz.api.recordings, "get", return_value={"recording": mb_ac}
    )
    mocker.patch.object(
        tasks.musicbrainz.api.releases, "get", return_value={"recording": mb_ac_album}
    )

    track = tasks.get_track_from_import_metadata(metadata)

    assert track.title == metadata["title"]
    assert track.mbid == metadata["mbid"]
    assert track.position == 4
    assert track.album == album
    assert track.artist_credit.all()[0] == artist_credit


def test_can_create_track_from_file_metadata_fid_existing_album_artist(
    factories, mocker
):
    artist = factories["music.Artist"]()
    album = factories["music.Album"]()
    metadata = {
        "artist_credit": [
            {"credit": "", "artist": {"fid": artist.fid}, "joinphrase": ""}
        ],
        "album": {
            "title": "",
            "fid": album.fid,
            "artist_credit": [
                {
                    "credit": "",
                    "joinphrase": "",
                    "artist": {
                        "name": "",
                        "fid": album.artist_credit.all()[0].artist.fid,
                    },
                }
            ],
        },
        "title": "Hello",
        "position": 4,
        "fid": "https://hello",
    }

    track = tasks.get_track_from_import_metadata(metadata)

    assert track.title == metadata["title"]
    assert track.fid == metadata["fid"]
    assert track.position == 4
    assert track.album == album
    assert track.artist_credit.all()[0].artist == artist


def test_can_create_track_from_file_metadata_distinct_release_mbid(factories, mocker):
    """Cf https://dev.funkwhale.audio/funkwhale/funkwhale/issues/772"""
    artist_credit = factories["music.ArtistCredit"]()
    album = factories["music.Album"](artist_credit=artist_credit)
    track = factories["music.Track"](album=album, artist_credit=artist_credit)
    metadata = {
        "artist_credit": [
            {
                "credit": artist_credit.artist.name,
                "mbid": artist_credit.artist.mbid,
                "joinphrase": "",
            }
        ],
        "album": {"title": album.title, "mbid": str(uuid.uuid4())},
        "title": track.title,
        "position": 4,
        "fid": "https://hello",
    }

    mb_ac_album = {
        "artist-credit": [
            {
                "artist": {
                    "id": artist_credit.artist.mbid,
                    "name": artist_credit.artist.name,
                },
                "name": artist_credit.artist.name,
            },
            "",
        ]
    }
    mocker.patch.object(
        tasks.musicbrainz.api.releases, "get", return_value={"recording": mb_ac_album}
    )
    new_track = tasks.get_track_from_import_metadata(metadata)

    # the returned track should be different from the existing one, and mapped
    # to a new album, because the albumid is different
    assert new_track.album != album
    assert new_track != track


def test_can_create_track_from_file_metadata_distinct_position(factories, mocker):
    """Cf https://dev.funkwhale.audio/funkwhale/funkwhale/issues/740"""
    artist_credit = factories["music.ArtistCredit"]()
    album = factories["music.Album"](artist_credit=artist_credit)
    track = factories["music.Track"](album=album, artist_credit=artist_credit)
    metadata = {
        "artist_credit": [
            {
                "credit": artist_credit.artist.name,
                "joinphrase": "",
                "mbid": artist_credit.artist.mbid,
            }
        ],
        "album": {"title": album.title, "mbid": album.mbid},
        "title": track.title,
        "position": track.position + 1,
    }
    mb_ac_album = {
        "artist-credit": [
            {
                "artist": {
                    "id": artist_credit.artist.mbid,
                    "name": artist_credit.artist.name,
                },
                "name": artist_credit.artist.name,
            },
            "",
        ]
    }
    mocker.patch.object(
        tasks.musicbrainz.api.releases, "get", return_value={"recording": mb_ac_album}
    )
    new_track = tasks.get_track_from_import_metadata(metadata)

    assert new_track != track


def test_can_create_track_from_file_metadata_federation(factories, mocker):
    metadata = {
        "artist_credit": [
            {
                "credit": "Artist",
                "artist": {
                    "name": "Artist",
                    "fid": "https://artist.fid",
                    "fdate": timezone.now(),
                },
                "credit": "Artist",
                "joinphrase": "",
            }
        ],
        "album": {
            "title": "Album",
            "fid": "https://album.fid",
            "fdate": timezone.now(),
            "cover_data": {"url": "https://cover/hello.png", "mimetype": "image/png"},
            "artist_credit": [
                {
                    "credit": "Album artist",
                    "artist": {
                        "name": "Album artist",
                        "fid": "https://album.artist.fid",
                        "fdate": timezone.now(),
                    },
                    "joinphrase": "",
                }
            ],
        },
        "title": "Hello",
        "position": 4,
        "fid": "https://hello",
        "fdate": timezone.now(),
    }

    track = tasks.get_track_from_import_metadata(metadata, update_cover=True)

    assert track.title == metadata["title"]
    assert track.fid == metadata["fid"]
    assert track.creation_date == metadata["fdate"]
    assert track.position == 4
    assert track.album.attachment_cover.url == metadata["album"]["cover_data"]["url"]
    assert (
        track.album.attachment_cover.mimetype
        == metadata["album"]["cover_data"]["mimetype"]
    )

    assert track.album.fid == metadata["album"]["fid"]
    assert track.album.title == metadata["album"]["title"]
    assert track.album.creation_date == metadata["album"]["fdate"]
    assert (
        track.album.artist_credit.all()[0].artist.fid
        == metadata["album"]["artist_credit"][0]["artist"].fid
    )
    assert (
        track.album.artist_credit.all()[0].artist.name
        == metadata["album"]["artist_credit"][0]["credit"]
    )
    assert (
        track.album.artist_credit.all()[0].artist.creation_date
        == metadata["album"]["artist_credit"][0]["artist"].creation_date
    )
    assert (
        track.artist_credit.all()[0].artist.fid
        == metadata["artist_credit"][0]["artist"].fid
    )
    assert (
        track.artist_credit.all()[0].artist.name
        == metadata["artist_credit"][0]["credit"]
    )
    assert (
        track.artist_credit.all()[0].artist.creation_date
        == metadata["artist_credit"][0]["artist"].creation_date
    )


def test_sort_candidates(factories):
    artist1 = factories["music.Artist"].build(fid=None, mbid=None)
    artist2 = factories["music.Artist"].build(fid=None)
    artist3 = factories["music.Artist"].build(mbid=None)
    result = tasks.sort_candidates([artist1, artist2, artist3], ["mbid", "fid"])

    assert result == [artist2, artist3, artist1]


def test_upload_import(now, factories, temp_signal, mocker):
    outbox = mocker.patch("funkwhale_api.federation.routes.outbox.dispatch")
    populate_album_cover = mocker.patch(
        "funkwhale_api.music.tasks.populate_album_cover"
    )
    get_picture = mocker.patch("funkwhale_api.music.metadata.Metadata.get_picture")
    get_track_from_import_metadata = mocker.spy(tasks, "get_track_from_import_metadata")
    track = factories["music.Track"](album__attachment_cover=None)
    upload = factories["music.Upload"](
        track=None, import_metadata={"funkwhale": {"track": {"uuid": str(track.uuid)}}}
    )
    create_entries = mocker.patch(
        "funkwhale_api.music.models.TrackActor.create_entries"
    )

    with temp_signal(signals.upload_import_status_updated) as handler:
        tasks.process_upload(upload_id=upload.pk)

    upload.refresh_from_db()

    assert upload.track == track
    assert upload.import_status == "finished"
    assert upload.import_date == now
    get_picture.assert_called_once_with("cover_front", "other")
    populate_album_cover.assert_called_once_with(
        upload.track.album, source=upload.source
    )
    assert (
        get_track_from_import_metadata.call_args[-1]["attributed_to"]
        == upload.library.actor
    )
    handler.assert_called_once_with(
        upload=upload,
        old_status="pending",
        new_status="finished",
        sender=None,
        signal=signals.upload_import_status_updated,
    )
    outbox.assert_called_once_with(
        {"type": "Create", "object": {"type": "Audio"}}, context={"upload": upload}
    )
    create_entries.assert_called_once_with(
        library=upload.library,
        delete_existing=False,
        upload_and_track_ids=[(upload.pk, upload.track_id)],
    )


def test_upload_import_get_audio_data(factories, mocker):
    mocker.patch(
        "funkwhale_api.music.models.Upload.get_audio_data",
        return_value={"size": 23, "duration": 42, "bitrate": 66},
    )
    track = factories["music.Track"](album__with_cover=True)
    upload = factories["music.Upload"](
        track=None, import_metadata={"funkwhale": {"track": {"uuid": track.uuid}}}
    )

    tasks.process_upload(upload_id=upload.pk)

    upload.refresh_from_db()
    assert upload.size == 23
    assert upload.duration == 42
    assert upload.bitrate == 66


def test_upload_import_in_place(factories, mocker):
    mocker.patch(
        "funkwhale_api.music.models.Upload.get_audio_data",
        return_value={"size": 23, "duration": 42, "bitrate": 66},
    )
    track = factories["music.Track"]()
    path = os.path.join(DATA_DIR, "test.ogg")
    upload = factories["music.Upload"](
        track=None,
        audio_file=None,
        source=f"file://{path}",
        import_metadata={"funkwhale": {"track": {"uuid": track.uuid}}},
    )

    tasks.process_upload(upload_id=upload.pk)

    upload.refresh_from_db()
    assert upload.size == 23
    assert upload.duration == 42
    assert upload.bitrate == 66
    assert upload.mimetype == "audio/ogg"


def test_upload_import_skip_existing_track_in_own_library(factories, temp_signal):
    track = factories["music.Track"]()
    library = factories["music.Library"]()
    existing = factories["music.Upload"](
        track=track,
        import_status="finished",
        library=library,
        import_metadata={"funkwhale": {"track": {"uuid": track.mbid}}},
    )
    duplicate = factories["music.Upload"](
        track=track,
        import_status="pending",
        library=library,
        import_metadata={"funkwhale": {"track": {"uuid": track.uuid}}},
    )
    with temp_signal(signals.upload_import_status_updated) as handler:
        tasks.process_upload(upload_id=duplicate.pk)

    duplicate.refresh_from_db()

    assert duplicate.import_status == "skipped"
    assert duplicate.import_details == {
        "code": "already_imported_in_owned_libraries",
        "duplicates": str(existing.uuid),
    }

    handler.assert_called_once_with(
        upload=duplicate,
        old_status="pending",
        new_status="skipped",
        sender=None,
        signal=signals.upload_import_status_updated,
    )


@pytest.mark.parametrize("import_status", ["draft", "errored", "finished"])
def test_process_upload_picks_ignore_non_pending_uploads(import_status, factories):
    upload = factories["music.Upload"](import_status=import_status)

    with pytest.raises(upload.DoesNotExist):
        tasks.process_upload(upload_id=upload.pk)


def test_upload_import_track_uuid(now, factories):
    track = factories["music.Track"](album__with_cover=True)
    upload = factories["music.Upload"](
        track=None, import_metadata={"funkwhale": {"track": {"uuid": track.uuid}}}
    )

    tasks.process_upload(upload_id=upload.pk)

    upload.refresh_from_db()

    assert upload.track == track
    assert upload.import_status == "finished"
    assert upload.import_date == now


def test_upload_import_skip_federation(now, factories, mocker):
    outbox = mocker.patch("funkwhale_api.federation.routes.outbox.dispatch")
    track = factories["music.Track"](album__with_cover=True)
    upload = factories["music.Upload"](
        track=None,
        import_metadata={
            "funkwhale": {
                "track": {"uuid": track.uuid},
                "config": {"dispatch_outbox": False},
            }
        },
    )

    tasks.process_upload(upload_id=upload.pk)

    outbox.assert_not_called()


def test_upload_import_skip_broadcast(now, factories, mocker):
    group_send = mocker.patch("funkwhale_api.common.channels.group_send")
    track = factories["music.Track"](album__with_cover=True)
    upload = factories["music.Upload"](
        library__actor__local=True,
        track=None,
        import_metadata={
            "funkwhale": {"track": {"uuid": track.uuid}, "config": {"broadcast": False}}
        },
    )

    tasks.process_upload(upload_id=upload.pk)

    group_send.assert_not_called()


def test_upload_import_error(factories, now, temp_signal):
    upload = factories["music.Upload"](
        import_metadata={"funkwhale": {"track": {"uuid": uuid.uuid4()}}}
    )
    with temp_signal(signals.upload_import_status_updated) as handler:
        tasks.process_upload(upload_id=upload.pk)
    upload.refresh_from_db()

    assert upload.import_status == "errored"
    assert upload.import_date == now
    assert upload.import_details == {
        "error_code": "track_uuid_not_found",
        "detail": None,
    }
    handler.assert_called_once_with(
        upload=upload,
        old_status="pending",
        new_status="errored",
        sender=None,
        signal=signals.upload_import_status_updated,
    )


def test_upload_import_error_metadata(factories, now, temp_signal, mocker):
    path = os.path.join(DATA_DIR, "test.ogg")
    upload = factories["music.Upload"](audio_file__frompath=path)
    mocker.patch.object(
        metadata.AlbumField,
        "to_internal_value",
        side_effect=metadata.serializers.ValidationError("Hello"),
    )
    with temp_signal(signals.upload_import_status_updated) as handler:
        tasks.process_upload(upload_id=upload.pk)
    upload.refresh_from_db()

    assert upload.import_status == "errored"
    assert upload.import_date == now
    assert upload.import_details == {
        "error_code": "invalid_metadata",
        "detail": {"album": ["Hello"]},
        "file_metadata": metadata.Metadata(path).all(),
    }
    handler.assert_called_once_with(
        upload=upload,
        old_status="pending",
        new_status="errored",
        sender=None,
        signal=signals.upload_import_status_updated,
    )


def test_upload_import_updates_cover_if_no_cover(factories, mocker, now):
    populate_album_cover = mocker.patch(
        "funkwhale_api.music.tasks.populate_album_cover"
    )
    album = factories["music.Album"](attachment_cover=None)
    track = factories["music.Track"](album=album)
    upload = factories["music.Upload"](
        track=None, import_metadata={"funkwhale": {"track": {"uuid": track.uuid}}}
    )
    tasks.process_upload(upload_id=upload.pk)
    populate_album_cover.assert_called_once_with(album, source=None)


@pytest.mark.parametrize("ext,mimetype", [("jpg", "image/jpeg"), ("png", "image/png")])
def test_populate_album_cover_file_cover_separate_file(
    ext, mimetype, factories, mocker
):
    mocker.patch("funkwhale_api.music.tasks.IMAGE_TYPES", [(ext, mimetype)])
    image_path = os.path.join(DATA_DIR, f"cover.{ext}")
    with open(image_path, "rb") as f:
        image_content = f.read()
    album = factories["music.Album"](attachment_cover=None, mbid=None)

    attach_file = mocker.patch("funkwhale_api.common.utils.attach_file")
    mocker.patch("funkwhale_api.music.metadata.Metadata.get_picture", return_value=None)
    tasks.populate_album_cover(album=album, source="file://" + image_path)
    attach_file.assert_called_once_with(
        album, "attachment_cover", {"mimetype": mimetype, "content": image_content}
    )


def test_federation_audio_track_to_metadata(now, mocker):
    published = now
    released = now.date()
    references = {
        "http://track.attributed": mocker.Mock(),
        "http://album.attributed": mocker.Mock(),
        "http://album-artist.attributed": mocker.Mock(),
        "http://artist.attributed": mocker.Mock(),
    }
    payload = {
        "@context": jsonld.get_default_context(),
        "type": "Track",
        "id": "http://hello.track",
        "musicbrainzId": str(uuid.uuid4()),
        "name": "Black in back",
        "position": 5,
        "disc": 2,
        "published": published.isoformat(),
        "license": "http://creativecommons.org/licenses/by-sa/4.0/",
        "copyright": "2018 Someone",
        "attributedTo": "http://track.attributed",
        "tag": [{"type": "Hashtag", "name": "TrackTag"}],
        "content": "hello there",
        "image": {
            "type": "Link",
            "href": "http://cover.test/track",
            "mediaType": "image/png",
        },
        "album": {
            "published": published.isoformat(),
            "type": "Album",
            "id": "http://hello.album",
            "name": "Purple album",
            "musicbrainzId": str(uuid.uuid4()),
            "released": released.isoformat(),
            "tag": [{"type": "Hashtag", "name": "AlbumTag"}],
            "attributedTo": "http://album.attributed",
            "content": "album desc",
            "mediaType": "text/plain",
            "artist_credit": [
                {
                    "artist": {
                        "type": "Artist",
                        "published": published.isoformat(),
                        "id": "http://hello.artist",
                        "name": "John Smith",
                        "content": "album artist desc",
                        "mediaType": "text/markdown",
                        "musicbrainzId": str(uuid.uuid4()),
                        "attributedTo": "http://album-artist.attributed",
                        "tag": [{"type": "Hashtag", "name": "AlbumArtistTag"}],
                        "image": {
                            "type": "Link",
                            "href": "http://cover.test/album-artist",
                            "mediaType": "image/png",
                        },
                    },
                    "joinphrase": "",
                    "id": "http://lol.fr",
                    "published": published.isoformat(),
                    "credit": "John Smith",
                }
            ],
            "image": {
                "type": "Link",
                "href": "http://cover.test",
                "mediaType": "image/png",
            },
        },
        "artist_credit": [
            {
                "artist": {
                    "published": published.isoformat(),
                    "type": "Artist",
                    "id": "http://hello.trackartist",
                    "name": "Bob Smith",
                    "content": "artist desc",
                    "mediaType": "text/html",
                    "musicbrainzId": str(uuid.uuid4()),
                    "attributedTo": "http://artist.attributed",
                    "tag": [{"type": "Hashtag", "name": "ArtistTag"}],
                    "image": {
                        "type": "Link",
                        "href": "http://cover.test/artist",
                        "mediaType": "image/png",
                    },
                },
                "joinphrase": "",
                "id": "http://loli.fr",
                "published": published.isoformat(),
                "credit": "Bob Smith",
            }
        ],
    }
    serializer = federation_serializers.TrackSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    expected = {
        "title": payload["name"],
        "position": payload["position"],
        "disc_number": payload["disc"],
        "license": "http://creativecommons.org/licenses/by-sa/4.0/",
        "copyright": "2018 Someone",
        "mbid": payload["musicbrainzId"],
        "fdate": serializer.validated_data["published"],
        "fid": payload["id"],
        "attributed_to": references["http://track.attributed"],
        "tags": ["TrackTag"],
        "description": {"content_type": "text/html", "text": "hello there"},
        "cover_data": {
            "mimetype": serializer.validated_data["image"]["mediaType"],
            "url": serializer.validated_data["image"]["href"],
        },
        "album": {
            "title": payload["album"]["name"],
            "attributed_to": references["http://album.attributed"],
            "release_date": released,
            "mbid": payload["album"]["musicbrainzId"],
            "fid": payload["album"]["id"],
            "fdate": serializer.validated_data["album"]["published"],
            "tags": ["AlbumTag"],
            "description": {"content_type": "text/plain", "text": "album desc"},
            "cover_data": {
                "mimetype": serializer.validated_data["album"]["image"]["mediaType"],
                "url": serializer.validated_data["album"]["image"]["href"],
            },
            "artist_credit": [
                {
                    "artist": {
                        "name": a["artist"]["name"],
                        "mbid": a["artist"]["musicbrainzId"],
                        "fid": a["artist"]["id"],
                        "attributed_to": references["http://album-artist.attributed"],
                        "fdate": serializer.validated_data["album"]["artist_credit"][i][
                            "artist"
                        ]["published"],
                        "description": {
                            "content_type": "text/markdown",
                            "text": "album artist desc",
                        },
                        "tags": ["AlbumArtistTag"],
                        "cover_data": {
                            "mimetype": serializer.validated_data["album"][
                                "artist_credit"
                            ][i]["artist"]["image"]["mediaType"],
                            "url": serializer.validated_data["album"]["artist_credit"][
                                i
                            ]["artist"]["image"]["href"],
                        },
                    },
                    "joinphrase": a["joinphrase"],
                    "credit": a["artist"]["name"],
                }
                for i, a in enumerate(payload["album"]["artist_credit"])
            ],
        },
        "artist_credit": [
            {
                "artist": {
                    "name": a["artist"]["name"],
                    "mbid": a["artist"]["musicbrainzId"],
                    "fid": a["artist"]["id"],
                    "fdate": serializer.validated_data["artist_credit"][i]["artist"][
                        "published"
                    ],
                    "attributed_to": references["http://artist.attributed"],
                    "tags": ["ArtistTag"],
                    "description": {"content_type": "text/html", "text": "artist desc"},
                    "cover_data": {
                        "mimetype": serializer.validated_data["artist_credit"][i][
                            "artist"
                        ]["image"]["mediaType"],
                        "url": serializer.validated_data["artist_credit"][i]["artist"][
                            "image"
                        ]["href"],
                    },
                },
                "joinphrase": "",
                "credit": a["artist"]["name"],
            }
            for i, a in enumerate(payload["artist_credit"])
        ],
    }

    result = tasks.federation_audio_track_to_metadata(
        serializer.validated_data, references
    )
    assert result == expected


def test_scan_library_fetches_page_and_calls_scan_page(now, mocker, factories, r_mock):
    scan = factories["music.LibraryScan"]()
    collection_conf = {
        "actor": scan.library.actor,
        "id": scan.library.fid,
        "page_size": 10,
        "items": range(10),
        "type": "Library",
        "name": "hello",
    }
    collection = federation_serializers.PaginatedCollectionSerializer(collection_conf)
    data = collection.data
    data["followers"] = "https://followers.domain"

    scan_page = mocker.patch("funkwhale_api.music.tasks.scan_library_page.delay")
    r_mock.get(collection_conf["id"], json=data)
    tasks.start_library_scan(library_scan_id=scan.pk)

    scan_page.assert_called_once_with(library_scan_id=scan.pk, page_url=data["first"])
    scan.refresh_from_db()

    assert scan.status == "scanning"
    assert scan.total_files == len(collection_conf["items"])
    assert scan.modification_date == now


def test_scan_page_fetches_page_and_creates_tracks(now, mocker, factories, r_mock):
    scan_page = mocker.patch("funkwhale_api.music.tasks.scan_library_page.delay")
    scan = factories["music.LibraryScan"](status="scanning", total_files=5)
    uploads = [
        factories["music.Upload"](
            fid=f"https://track.test/{i}",
            size=42,
            bitrate=66,
            duration=99,
            library=scan.library,
            track__album__with_cover=True,
        )
        for i in range(5)
    ]

    page_conf = {
        "actor": scan.library.actor,
        "id": scan.library.fid,
        "page": Paginator(uploads, 3).page(1),
        "item_serializer": federation_serializers.UploadSerializer,
    }
    uploads[0].__class__.objects.filter(pk__in=[u.pk for u in uploads]).delete()
    page = federation_serializers.CollectionPageSerializer(page_conf)

    r_mock.get(page.data["id"], json=page.data)

    tasks.scan_library_page(library_scan_id=scan.pk, page_url=page.data["id"])

    scan.refresh_from_db()
    lts = list(scan.library.uploads.all().order_by("-creation_date"))

    assert len(lts) == 3
    for upload in uploads[:3]:
        scan.library.uploads.get(fid=upload.fid)

    assert scan.status == "scanning"
    assert scan.processed_files == 3
    assert scan.modification_date == now

    scan_page.assert_called_once_with(
        library_scan_id=scan.pk, page_url=page.data["next"]
    )


def test_scan_page_trigger_next_page_scan_skip_if_same(mocker, factories, r_mock):
    patched_scan = mocker.patch("funkwhale_api.music.tasks.scan_library_page.delay")
    scan = factories["music.LibraryScan"](status="scanning", total_files=5)
    uploads = factories["music.Upload"].build_batch(size=5, library=scan.library)
    page_conf = {
        "actor": scan.library.actor,
        "id": scan.library.fid,
        "page": Paginator(uploads, 3).page(1),
        "item_serializer": federation_serializers.UploadSerializer,
    }
    page = federation_serializers.CollectionPageSerializer(page_conf)
    data = page.data
    data["next"] = data["id"]
    r_mock.get(page.data["id"], json=data)

    tasks.scan_library_page(library_scan_id=scan.pk, page_url=data["id"])
    patched_scan.assert_not_called()
    scan.refresh_from_db()

    assert scan.status == "finished"


def test_clean_transcoding_cache(preferences, now, factories):
    preferences["music__transcoding_cache_duration"] = 60
    u1 = factories["music.UploadVersion"](
        accessed_date=now - datetime.timedelta(minutes=61)
    )
    u2 = factories["music.UploadVersion"](
        accessed_date=now - datetime.timedelta(minutes=59)
    )

    tasks.clean_transcoding_cache()

    u2.refresh_from_db()

    with pytest.raises(u1.__class__.DoesNotExist):
        u1.refresh_from_db()


def test_get_prunable_tracks(factories):
    prunable_track = factories["music.Track"]()
    # track is still prunable if it has a skipped upload linked to it
    factories["music.Upload"](import_status="skipped", track=prunable_track)
    # non prunable tracks
    factories["music.Upload"]()
    factories["favorites.TrackFavorite"]()
    factories["history.Listening"]()
    factories["playlists.PlaylistTrack"]()

    assert list(tasks.get_prunable_tracks()) == [prunable_track]


def test_get_prunable_tracks_include_favorites(factories):
    prunable_track = factories["music.Track"]()
    favorited = factories["favorites.TrackFavorite"]().track
    # non prunable tracks
    factories["favorites.TrackFavorite"](track__playable=True)
    factories["music.Upload"]()
    factories["history.Listening"]()
    factories["playlists.PlaylistTrack"]()

    qs = tasks.get_prunable_tracks(exclude_favorites=False).order_by("id")
    assert list(qs) == [prunable_track, favorited]


def test_get_prunable_tracks_include_playlists(factories):
    prunable_track = factories["music.Track"]()
    in_playlist = factories["playlists.PlaylistTrack"]().track
    # non prunable tracks
    factories["favorites.TrackFavorite"]()
    factories["music.Upload"]()
    factories["history.Listening"]()
    factories["playlists.PlaylistTrack"](track__playable=True)

    qs = tasks.get_prunable_tracks(exclude_playlists=False).order_by("id")
    assert list(qs) == [prunable_track, in_playlist]


def test_get_prunable_tracks_include_listenings(factories):
    prunable_track = factories["music.Track"]()
    listened = factories["history.Listening"]().track
    # non prunable tracks
    factories["favorites.TrackFavorite"]()
    factories["music.Upload"]()
    factories["history.Listening"](track__playable=True)
    factories["playlists.PlaylistTrack"]()

    qs = tasks.get_prunable_tracks(exclude_listenings=False).order_by("id")
    assert list(qs) == [prunable_track, listened]


def test_get_prunable_albums(factories):
    prunable_album = factories["music.Album"]()
    # non prunable album
    factories["music.Track"]().album

    assert list(tasks.get_prunable_albums()) == [prunable_album]


def test_get_prunable_artists(factories):
    prunable_artist = factories["music.Artist"]()
    # non prunable artist
    non_prunable_artist = factories["music.Artist"]()
    non_prunable_album_artist = factories["music.Artist"]()
    factories["music.Track"](artist_credit__artist=non_prunable_artist)
    factories["music.Track"](album__artist_credit__artist=non_prunable_album_artist)

    assert list(tasks.get_prunable_artists()) == [prunable_artist]


def test_update_library_entity(factories, mocker):
    artist = factories["music.Artist"]()
    save = mocker.spy(artist, "save")

    tasks.update_library_entity(artist, {"name": "Hello"})
    save.assert_called_once_with(update_fields=["name"])

    artist.refresh_from_db()
    assert artist.name == "Hello"


@pytest.mark.parametrize(
    "name, ext, mimetype",
    [
        ("cover", "png", "image/png"),
        ("cover", "jpg", "image/jpeg"),
        ("cover", "jpeg", "image/jpeg"),
        ("folder", "png", "image/png"),
        ("folder", "jpg", "image/jpeg"),
        ("folder", "jpeg", "image/jpeg"),
    ],
)
def test_get_cover_from_fs(name, ext, mimetype, tmpdir):
    cover_path = os.path.join(tmpdir, f"{name}.{ext}")
    content = "Hello"
    with open(cover_path, "w") as f:
        f.write(content)

    expected = {"mimetype": mimetype, "content": content.encode()}
    assert tasks.get_cover_from_fs(tmpdir) == expected


@pytest.mark.parametrize("name", ["cover.gif", "folder.gif"])
def test_get_cover_from_fs_ignored(name, tmpdir):
    cover_path = os.path.join(tmpdir, name)
    content = "Hello"
    with open(cover_path, "w") as f:
        f.write(content)

    assert tasks.get_cover_from_fs(tmpdir) is None


def test_get_track_from_import_metadata_with_forced_values(factories, mocker, faker):
    actor = factories["federation.Actor"]()
    forced_values = {
        "title": "Real title",
        "artist": factories["music.Artist"](),
        "album": None,
        "license": factories["music.License"](),
        "position": 3,
        "copyright": "Real copyright",
        "mbid": faker.uuid4(),
        "attributed_to": actor,
        "tags": ["hello", "world"],
    }
    metadata = {
        "title": "Test track",
        "artist_credit": [{"name": "Test artist"}],
        "album": {"title": "Test album", "release_date": datetime.date(2012, 8, 15)},
        "position": 4,
        "disc_number": 2,
        "copyright": "2018 Someone",
        "tags": ["foo", "bar"],
    }

    track = tasks.get_track_from_import_metadata(metadata, **forced_values)

    assert track.title == forced_values["title"]
    assert track.mbid == forced_values["mbid"]
    assert track.position == forced_values["position"]
    assert track.disc_number == metadata["disc_number"]
    assert track.copyright == forced_values["copyright"]
    assert track.album == forced_values["album"]
    assert track.artist_credit.all()[0].artist == forced_values["artist"]
    assert track.attributed_to == forced_values["attributed_to"]
    assert track.license == forced_values["license"]
    assert (
        sorted(track.tagged_items.values_list("tag__name", flat=True))
        == forced_values["tags"]
    )


def test_get_track_from_import_metadata_with_forced_values_album(
    factories, mocker, faker
):
    channel = factories["audio.Channel"]()
    album = factories["music.Album"](
        artist_credit__artist=channel.artist, with_cover=True
    )

    forced_values = {
        "title": "Real title",
        "album": album.pk,
    }
    upload = factories["music.Upload"](
        import_metadata=forced_values, library=channel.library, track=None
    )

    tasks.process_upload(upload_id=upload.pk)
    upload.refresh_from_db()
    assert upload.import_status == "finished"

    assert upload.track.title == forced_values["title"]
    assert upload.track.album == album
    assert upload.track.artist_credit.all()[0].artist == channel.artist


def test_process_channel_upload_forces_artist_and_attributed_to(
    factories, mocker, faker
):
    channel = factories["audio.Channel"](attributed_to__local=True)
    update_modification_date = mocker.spy(common_utils, "update_modification_date")

    attachment = factories["common.Attachment"](actor=channel.attributed_to)
    import_metadata = {
        "title": "Real title",
        "position": 3,
        "copyright": "Real copyright",
        "tags": ["hello", "world"],
        "description": "my description",
        "cover": attachment.uuid,
    }
    expected_forced_values = import_metadata.copy()
    expected_forced_values["artist"] = channel.artist
    expected_forced_values["cover"] = attachment
    upload = factories["music.Upload"](
        track=None, import_metadata=import_metadata, library=channel.library
    )
    get_track_from_import_metadata = mocker.spy(tasks, "get_track_from_import_metadata")

    tasks.process_upload(upload_id=upload.pk)

    upload.refresh_from_db()

    expected_final_metadata = tasks.collections.ChainMap(
        {"upload_source": None},
        expected_forced_values,
        {"funkwhale": {}},
    )
    assert upload.import_status == "finished"
    get_track_from_import_metadata.assert_called_once_with(
        expected_final_metadata,
        attributed_to=channel.attributed_to,
        **expected_forced_values,
    )

    assert upload.track.description.content_type == "text/markdown"
    assert upload.track.description.text == import_metadata["description"]
    assert upload.track.title == import_metadata["title"]
    assert upload.track.position == import_metadata["position"]
    assert upload.track.copyright == import_metadata["copyright"]
    assert upload.track.get_tags() == import_metadata["tags"]
    assert upload.track.artist_credit.all()[0].artist == channel.artist
    assert upload.track.attributed_to == channel.attributed_to
    assert upload.track.attachment_cover == attachment

    update_modification_date.assert_called_once_with(channel.artist)


def test_process_upload_uses_import_metadata_if_valid(factories, mocker):
    track = factories["music.Track"](album__with_cover=True)
    import_metadata = {"title": "hello", "funkwhale": {"foo": "bar"}}
    upload = factories["music.Upload"](track=None, import_metadata=import_metadata)
    get_track_from_import_metadata = mocker.patch.object(
        tasks, "get_track_from_import_metadata", return_value=track
    )
    tasks.process_upload(upload_id=upload.pk)

    serializer = tasks.metadata.TrackMetadataSerializer(
        data=tasks.metadata.Metadata(upload.get_audio_file())
    )
    assert serializer.is_valid() is True
    audio_metadata = serializer.validated_data

    expected_final_metadata = tasks.collections.ChainMap(
        {"upload_source": None},
        audio_metadata,
        {"funkwhale": import_metadata["funkwhale"]},
    )
    get_track_from_import_metadata.assert_called_once_with(
        expected_final_metadata, attributed_to=upload.library.actor, title="hello"
    )


def test_process_upload_skips_import_metadata_if_invalid(factories, mocker):
    track = factories["music.Track"](album__with_cover=True)
    import_metadata = {"title": None, "funkwhale": {"foo": "bar"}}
    upload = factories["music.Upload"](track=None, import_metadata=import_metadata)
    get_track_from_import_metadata = mocker.patch.object(
        tasks, "get_track_from_import_metadata", return_value=track
    )
    tasks.process_upload(upload_id=upload.pk)

    serializer = tasks.metadata.TrackMetadataSerializer(
        data=tasks.metadata.Metadata(upload.get_audio_file())
    )
    assert serializer.is_valid() is True
    audio_metadata = serializer.validated_data

    expected_final_metadata = tasks.collections.ChainMap(
        {"upload_source": None},
        audio_metadata,
        {"funkwhale": import_metadata["funkwhale"]},
    )
    get_track_from_import_metadata.assert_called_once_with(
        expected_final_metadata, attributed_to=upload.library.actor
    )


def test_tag_albums_from_tracks(queryset_equal_queries, factories, mocker):
    get_tags_from_foreign_key = mocker.patch(
        "funkwhale_api.tags.tasks.get_tags_from_foreign_key"
    )
    add_tags_batch = mocker.patch("funkwhale_api.tags.tasks.add_tags_batch")

    expected_queryset = (
        federation_utils.local_qs(
            models.Album.objects.filter(tagged_items__isnull=True)
        )
        .values_list("id", flat=True)
        .order_by("id")
    )
    tasks.albums_set_tags_from_tracks(ids=[1, 2])
    get_tags_from_foreign_key.assert_called_once_with(
        ids=expected_queryset.filter(pk__in=[1, 2]),
        foreign_key_model=models.Track,
        foreign_key_attr="album",
    )

    add_tags_batch.assert_called_once_with(
        get_tags_from_foreign_key.return_value,
        model=models.Album,
    )


def test_tag_artists_from_tracks(queryset_equal_queries, factories, mocker):
    get_tags_from_foreign_key = mocker.patch(
        "funkwhale_api.tags.tasks.get_tags_from_foreign_key"
    )
    add_tags_batch = mocker.patch("funkwhale_api.tags.tasks.add_tags_batch")

    expected_queryset = (
        federation_utils.local_qs(
            models.Artist.objects.filter(tagged_items__isnull=True)
        )
        .values_list("id", flat=True)
        .order_by("id")
    )
    tasks.artists_set_tags_from_tracks(ids=[1, 2])
    get_tags_from_foreign_key.assert_called_once_with(
        ids=expected_queryset.filter(pk__in=[1, 2]),
        foreign_key_model=models.Track,
        foreign_key_attr="artist",
    )

    add_tags_batch.assert_called_once_with(
        get_tags_from_foreign_key.return_value,
        model=models.Artist,
    )


def test_can_download_image_file_for_album_mbid(binary_cover, mocker, factories):
    mocker.patch(
        "funkwhale_api.musicbrainz.api.images.get_front", return_value=binary_cover
    )
    # client._api.get_image_front('55ea4f82-b42b-423e-a0e5-290ccdf443ed')
    album = factories["music.Album"](mbid="55ea4f82-b42b-423e-a0e5-290ccdf443ed")
    tasks.populate_album_cover(album, replace=True)

    assert album.attachment_cover.file.read() == binary_cover
    assert album.attachment_cover.mimetype == "image/jpeg"


def test_can_import_track_with_same_mbid_in_different_albums(factories, mocker):
    artist = factories["music.Artist"]()
    artist_credit = factories["music.ArtistCredit"](artist=artist)
    upload = factories["music.Upload"](
        playable=True,
        track__artist_credit=artist_credit,
        track__album__artist_credit=artist_credit,
    )
    assert upload.track.mbid is not None
    data = {
        "title": upload.track.title,
        "artist_credit": [{"credit": artist.name, "mbid": artist.mbid}],
        "album": {
            "title": "The Slip",
            "mbid": uuid.UUID("12b57d46-a192-499e-a91f-7da66790a1c1"),
            "release_date": datetime.date(2008, 5, 5),
            "artist_credit": [{"credit": artist.name, "mbid": artist.mbid}],
        },
        "position": 1,
        "disc_number": 1,
        "mbid": upload.track.mbid,
    }

    mb_ac = {
        "artist-credit": [
            {
                "artist": {
                    "id": artist.mbid,
                    "name": artist.name,
                },
                "joinphrase": "",
                "name": artist.name,
            },
        ]
    }
    mb_ac_album = {
        "artist-credit": [
            {
                "artist": {
                    "id": artist.mbid,
                    "name": artist.name,
                },
                "name": artist.name,
            },
        ]
    }

    mocker.patch.object(
        tasks.musicbrainz.api.recordings, "get", return_value={"recording": mb_ac}
    )
    mocker.patch.object(
        tasks.musicbrainz.api.releases, "get", return_value={"recording": mb_ac_album}
    )
    mocker.patch.object(metadata.TrackMetadataSerializer, "validated_data", data)
    mocker.patch.object(tasks, "populate_album_cover")

    new_upload = factories["music.Upload"](library=upload.library)

    tasks.process_upload(upload_id=new_upload.pk)

    new_upload.refresh_from_db()

    assert new_upload.import_status == "finished"


def test_import_track_with_same_mbid_in_same_albums_skipped(factories, mocker):
    artist = factories["music.Artist"]()
    artist_credit = factories["music.ArtistCredit"](artist=artist)

    upload = factories["music.Upload"](
        playable=True,
        track__artist_credit=artist_credit,
        track__album__artist_credit=artist_credit,
    )
    assert upload.track.mbid is not None
    data = {
        "title": upload.track.title,
        "artist_credit": [{"name": artist.name, "mbid": artist.mbid}],
        "album": {
            "title": upload.track.album.title,
            "mbid": upload.track.album.mbid,
            "artist_credit": [{"name": artist.name, "mbid": artist.mbid}],
        },
        "position": 1,
        "disc_number": 1,
        "mbid": upload.track.mbid,
    }

    mocker.patch.object(metadata.TrackMetadataSerializer, "validated_data", data)
    mocker.patch.object(tasks, "populate_album_cover")

    new_upload = factories["music.Upload"](library=upload.library)

    tasks.process_upload(upload_id=new_upload.pk)

    new_upload.refresh_from_db()

    assert new_upload.import_status == "skipped"


def test_can_import_track_with_same_position_in_different_discs(factories, mocker):
    upload = factories["music.Upload"](playable=True)
    artist_credit_data = [
        {
            "credit": upload.track.album.artist_credit.all()[0].artist.name,
            "mbid": upload.track.album.artist_credit.all()[0].artist.mbid,
            "joinphrase": "",
        }
    ]
    data = {
        "title": upload.track.title,
        "artist_credit": artist_credit_data,
        "album": {
            "title": "The Slip",
            "mbid": upload.track.album.mbid,
            "release_date": datetime.date(2008, 5, 5),
            "artist_credit": artist_credit_data,
        },
        "position": upload.track.position,
        "disc_number": 2,
        "mbid": None,
    }
    mb_ac_album = {
        "artist-credit": [
            {
                "artist": {
                    "id": upload.track.album.artist_credit.all()[0].artist.mbid,
                    "name": upload.track.album.artist_credit.all()[0].artist.name,
                },
            },
            "",
        ]
    }
    mocker.patch.object(metadata.TrackMetadataSerializer, "validated_data", data)
    mocker.patch.object(tasks, "populate_album_cover")
    mocker.patch.object(
        tasks.musicbrainz.api.releases, "get", return_value={"recording": mb_ac_album}
    )
    new_upload = factories["music.Upload"](library=upload.library)

    tasks.process_upload(upload_id=new_upload.pk)

    new_upload.refresh_from_db()

    assert new_upload.import_status == "finished"


def test_can_import_track_with_same_position_in_same_discs_skipped(factories, mocker):
    ac = factories["music.ArtistCredit"](joinphrase="", index=0)
    upload = factories["music.Upload"](
        playable=True, track__artist_credit=ac, track__album__artist_credit=ac
    )
    artist_data = [
        {
            "credit": upload.track.album.artist_credit.all()[0].artist.name,
            "mbid": upload.track.album.artist_credit.all()[0].artist.mbid,
            "joinphrase": "",
        }
    ]

    data = {
        "title": upload.track.title,
        "artist_credit": artist_data,
        "album": {
            "title": "The Slip",
            "mbid": upload.track.album.mbid,
            "release_date": datetime.date(2008, 5, 5),
            "artist_credit": artist_data,
        },
        "position": upload.track.position,
        "disc_number": upload.track.disc_number,
        "mbid": None,
    }
    mb_ac_album = {
        "artist-credit": [
            {
                "artist": {
                    "id": upload.track.album.artist_credit.all()[0].artist.mbid,
                    "name": upload.track.album.artist_credit.all()[0].artist.name,
                },
                "name": upload.track.album.artist_credit.all()[0].artist.name,
            },
            "",
        ]
    }
    mocker.patch.object(
        tasks.musicbrainz.api.releases, "get", return_value={"recording": mb_ac_album}
    )
    mocker.patch.object(metadata.TrackMetadataSerializer, "validated_data", data)
    mocker.patch.object(tasks, "populate_album_cover")

    new_upload = factories["music.Upload"](library=upload.library)

    tasks.process_upload(upload_id=new_upload.pk)

    new_upload.refresh_from_db()

    assert new_upload.import_status == "skipped"


def test_update_track_metadata_no_mbid(factories):
    track = factories["music.Track"]()
    data = {
        "title": "Peer Gynt Suite no. 1, op. 46: I. Morning",
        "artist": "Edvard Grieg",
        "album_artist": "Edvard Grieg; Musopen Symphony Orchestra",
        "album": "Peer Gynt Suite no. 1, op. 46",
        "date": "2012-08-15",
        "position": "4",
        "disc_number": "2",
        "license": "Dummy license: http://creativecommons.org/licenses/by-sa/4.0/",
        "copyright": "Someone",
        "comment": "hello there",
        "genre": "classical",
    }

    tasks.update_track_metadata(metadata.FakeMetadata(data), track)

    track.refresh_from_db()

    assert track.title == data["title"]
    assert track.position == int(data["position"])
    assert track.disc_number == int(data["disc_number"])
    assert track.license.code == "cc-by-sa-4.0"
    assert track.copyright == data["copyright"]
    assert track.album.title == data["album"]
    assert track.album.release_date == datetime.date(2012, 8, 15)
    assert track.get_artist_credit_string == data["artist"]
    assert track.artist_credit.all()[0].artist.mbid is None
    assert (
        track.album.get_artist_credit_string
        == "Edvard Grieg; Musopen Symphony Orchestra"
    )
    assert track.album.artist_credit.all()[0].artist.mbid is None
    assert sorted(track.tagged_items.values_list("tag__name", flat=True)) == [
        "classical"
    ]


def test_update_track_metadata_mbid(factories, mocker):
    track = factories["music.Track"]()
    factories["music.Artist"](
        name="Edvard Grieg", mbid="013c8e5b-d72a-4cd3-8dee-6c64d6125823"
    )
    data = {
        "title": "Peer Gynt Suite no. 1, op. 46: I. Morning",
        "artist": "Edvard Grieg",
        "album_artist": "Edvard Grieg; Musopen Symphony Orchestra",
        "album": "Peer Gynt Suite no. 1, op. 46",
        "date": "2012-08-15",
        "position": "4",
        "disc_number": "2",
        "musicbrainz_albumid": "a766da8b-8336-47aa-a3ee-371cc41ccc75",
        "mbid": "bd21ac48-46d8-4e78-925f-d9cc2a294656",
        "musicbrainz_artistid": "013c8e5b-d72a-4cd3-8dee-6c64d6125823",
        "musicbrainz_albumartistid": "013c8e5b-d72a-4cd3-8dee-6c64d6125823;5b4d7d2d-36df-4b38-95e3-a964234f520f",
        "license": "Dummy license: http://creativecommons.org/licenses/by-sa/4.0/",
        "copyright": "Someone",
        "comment": "hello there",
        "genre": "classical",
    }
    mb_ac = {
        "artist-credit": [
            {
                "artist": {
                    "id": "013c8e5b-d72a-4cd3-8dee-6c64d6125823",
                    "name": "Edvard Grieg",
                },
                "joinphrase": "",
                "name": "Edvard Grieg",
            }
        ]
    }

    mb_ac_album = {
        "artist-credit": [
            {
                "artist": {
                    "id": "013c8e5b-d72a-4cd3-8dee-6c64d6125823",
                    "name": "Edvard Grieg",
                },
            },
            "; ",
            {
                "artist": {
                    "id": "5b4d7d2d-36df-4b38-95e3-a964234f520f",
                    "name": "Musopen Symphony Orchestra",
                },
                "joinphrase": "",
                "name": "Musopen Symphony Orchestra",
            },
        ]
    }

    mocker.patch.object(
        tasks.musicbrainz.api.releases, "get", return_value={"recording": mb_ac_album}
    )
    mocker.patch.object(
        tasks.musicbrainz.api.recordings, "get", return_value={"recording": mb_ac}
    )
    tasks.update_track_metadata(metadata.FakeMetadata(data), track)

    track.refresh_from_db()

    assert track.title == data["title"]
    assert track.position == int(data["position"])
    assert track.disc_number == int(data["disc_number"])
    assert track.license.code == "cc-by-sa-4.0"
    assert track.copyright == data["copyright"]
    assert str(track.mbid) == data["mbid"]
    assert track.album.title == data["album"]
    assert track.album.release_date == datetime.date(2012, 8, 15)
    assert str(track.album.mbid) == data["musicbrainz_albumid"]
    assert track.get_artist_credit_string == data["artist"]
    assert (
        str(track.artist_credit.all()[0].artist.mbid)
        == "013c8e5b-d72a-4cd3-8dee-6c64d6125823"
    )
    assert (
        track.album.get_artist_credit_string
        == "Edvard Grieg; Musopen Symphony Orchestra"
    )
    assert (
        str(track.album.artist_credit.all()[0].artist.mbid)
        == "013c8e5b-d72a-4cd3-8dee-6c64d6125823"
    )
    assert sorted(track.tagged_items.values_list("tag__name", flat=True)) == [
        "classical"
    ]


def test_fs_import_not_pending(factories):
    with pytest.raises(ValueError):
        tasks.fs_import(
            library_id=factories["music.Library"]().pk,
            path="path",
            import_reference="test",
        )


def test_fs_import(factories, cache, mocker, settings):
    _handle = mocker.spy(tasks.import_files.Command, "_handle")
    cache.set("fs-import:status", "pending")
    library = factories["music.Library"](actor__local=True)
    tasks.fs_import(library_id=library.pk, path="path", import_reference="test")
    assert _handle.call_args[1] == {
        "recursive": True,
        "path": [settings.MUSIC_DIRECTORY_PATH + "/path"],
        "library_id": str(library.uuid),
        "update_cache": True,
        "in_place": True,
        "reference": "test",
        "watch": False,
        "interactive": False,
        "batch_size": 1000,
        "async_": False,
        "prune": True,
        "broadcast": False,
        "outbox": False,
        "exit_on_failure": False,
        "replace": False,
        "verbosity": 1,
    }
    assert cache.get("fs-import:status") == "finished"
    assert "Pruning dangling tracks" in cache.get("fs-import:logs")[-1]


def test_upload_checks_mbid_tag(temp_signal, factories, mocker, preferences):
    preferences["music__only_allow_musicbrainz_tagged_files"] = True
    mocker.patch("funkwhale_api.federation.routes.outbox.dispatch")
    mocker.patch("funkwhale_api.music.tasks.populate_album_cover")
    mocker.patch("funkwhale_api.music.metadata.Metadata.get_picture")
    track = factories["music.Track"](album__attachment_cover=None, mbid=None)
    path = os.path.join(DATA_DIR, "with_cover.opus")

    upload = factories["music.Upload"](
        track=None,
        audio_file__from_path=path,
        import_metadata={"funkwhale": {"track": {"uuid": str(track.uuid)}}},
    )
    mocker.patch("funkwhale_api.music.models.TrackActor.create_entries")

    with temp_signal(signals.upload_import_status_updated):
        tasks.process_upload(upload_id=upload.pk)

    upload.refresh_from_db()

    assert upload.import_status == "errored"
    assert upload.import_details == {
        "error_code": "Only content tagged with a MusicBrainz ID is permitted on this pod.",
        "detail": "You can tag your files with MusicBrainz Picard",
    }


def test_upload_checks_mbid_tag_pass(temp_signal, factories, mocker, preferences):
    preferences["music__only_allow_musicbrainz_tagged_files"] = True
    mocker.patch("funkwhale_api.federation.routes.outbox.dispatch")
    mocker.patch("funkwhale_api.music.tasks.populate_album_cover")
    mocker.patch("funkwhale_api.music.metadata.Metadata.get_picture")
    track = factories["music.Track"](album__attachment_cover=None, mbid=None)
    path = os.path.join(DATA_DIR, "test.mp3")

    upload = factories["music.Upload"](
        track=None,
        audio_file__from_path=path,
        import_metadata={"funkwhale": {"track": {"uuid": str(track.uuid)}}},
    )
    mocker.patch("funkwhale_api.music.models.TrackActor.create_entries")

    with temp_signal(signals.upload_import_status_updated):
        tasks.process_upload(upload_id=upload.pk)

    upload.refresh_from_db()

    assert upload.import_status == "finished"


@pytest.mark.parametrize(
    "raw_string, expected",
    [
        (
            "The Kinks|Various Artists",
            [("The Kinks", "|", 0, None), ("Various Artists", "", 1, None)],
        ),
        (
            "The Kinks,Various Artists",
            [("The Kinks", ",", 0, None), ("Various Artists", "", 1, None)],
        ),
        (
            "Luigi 21 Plus feat. Ñejo feat Ñengo Flow & Chyno Nyno with Linkin Park and Evanescance",
            [
                ("Luigi 21 Plus", " feat. ", 0, None),
                ("Ñejo", " feat ", 1, None),
                ("Ñengo Flow", " & ", 2, None),
                ("Chyno Nyno", " with ", 3, None),
                ("Linkin Park", " and ", 4, None),
                ("Evanescance", "", 5, None),
            ],
        ),
        (
            "Bad Bunny x Poeta Callejero ; Mark B (Carlos Serrano & Carlos Martin Mambo Remix)",
            [
                ("Bad Bunny", " x ", 0, None),
                ("Poeta Callejero", " ; ", 1, None),
                ("Mark B", " (", 2, None),
                ("Carlos Serrano", " & ", 3, None),
                ("Carlos Martin Mambo", " Remix)", 4, None),
            ],
        ),
    ],
)
def test_can_parse_multiples_artist(raw_string, expected):
    artist_credit = tasks.parse_credits(raw_string, None, None)
    assert artist_credit == expected


def test_get_best_candidate_or_create_find_artist_credit(factories):
    track = factories["music.Track"]()
    query = Q(
        title__iexact=track.title,
        artist_credit__in=track.artist_credit.all(),
        position=track.position,
        disc_number=track.disc_number,
    )
    defaults = "lol"
    tasks.get_best_candidate_or_create(
        models.Track, query, defaults=defaults, sort_fields=["mbid", "fid"]
    )


def test_get_or_create_artists_credits_from_musicbrainz(factories, mocker):
    release_mb_response = {
        "status": "Official",
        "status-id": "4e304316-386d-3409-af2e-78857eec5cfe",
        "country": "XW",
        "text-representation": {"script": "Latn", "language": "spa"},
        "release-events": [
            {
                "date": "2019-05-30",
                "area": {
                    "sort-name": "[Worldwide]",
                    "id": "525d4e18-3d00-31b9-a58b-a146a916de8f",
                    "disambiguation": "",
                    "iso-3166-1-codes": ["XW"],
                    "name": "[Worldwide]",
                },
            }
        ],
        "disambiguation": "",
        "cover-art-archive": {
            "front": True,
            "count": 1,
            "back": False,
            "darkened": False,
            "artwork": True,
        },
        "id": "48cc978e-17b8-46ab-91e8-3dceef2725b5",
        "packaging-id": "119eba76-b343-3e02-a292-f0f00644bb9b",
        "packaging": "None",
        "date": "2019-05-30",
        "title": "#TBT",
        "artist-credit": [
            {
                "joinphrase": "",
                "artist": {
                    "type-id": "b6e035f4-3ce9-331c-97df-83397230b0df",
                    "disambiguation": 'Hiram David Santos Rojas, reggaeton artist aka "Lui-G 21+"',
                    "name": "Luigi 21 Plus",
                    "type": "Person",
                    "sort-name": "Luigi 21 Plus",
                    "id": "f1642d37-bbe2-4aff-a75e-86845ff49fa4",
                },
                "name": "Luigi 21 Plus",
            }
        ],
        "quality": "normal",
    }
    recording_mb_response = {
        "length": 337000,
        "first-release-date": "2019-05-30",
        "disambiguation": "",
        "id": "cf3dacb7-3cee-430f-b0bb-cc4557158a03",
        "title": "Mueve ese culo puñeta",
        "artist-credit": [
            {
                "joinphrase": " feat. ",
                "artist": {
                    "type": "Person",
                    "id": "f1642d37-bbe2-4aff-a75e-86845ff49fa4",
                    "sort-name": "Luigi 21 Plus",
                    "type-id": "b6e035f4-3ce9-331c-97df-83397230b0df",
                    "name": "Luigi 21 Plus",
                    "disambiguation": 'Hiram David Santos Rojas, reggaeton artist aka "Lui-G 21+"',
                },
                "name": "Luigi 21 Plus",
            },
            {
                "name": "Ñejo",
                "artist": {
                    "type": "Person",
                    "id": "8248c905-689d-4e36-9def-7c515c5ef5eb",
                    "name": "Ñejo",
                    "disambiguation": "",
                    "sort-name": "Ñejo",
                    "type-id": "b6e035f4-3ce9-331c-97df-83397230b0df",
                },
                "joinphrase": ", ",
            },
            {
                "joinphrase": " & ",
                "artist": {
                    "type": "Person",
                    "id": "b7f5054e-c9de-49d8-b0eb-6deefb89b86b",
                    "name": "Ñengo Flow",
                    "disambiguation": "",
                    "type-id": "b6e035f4-3ce9-331c-97df-83397230b0df",
                    "sort-name": "Ñengo Flow",
                },
                "name": "Ñengo Flow",
            },
            {
                "joinphrase": "",
                "artist": {
                    "id": "3d50191b-820c-4f6f-b25a-bc12d63e6718",
                    "type": "Person",
                    "type-id": "b6e035f4-3ce9-331c-97df-83397230b0df",
                    "sort-name": "Chyno Nyno",
                    "disambiguation": "",
                    "name": "Chyno Nyno",
                },
                "name": "Chyno Nyno",
            },
        ],
        "video": False,
    }
    for mb_type, mb_response in [
        ("release", release_mb_response),
        ("recording", recording_mb_response),
    ]:
        mocker.patch.object(
            tasks.musicbrainz.api.releases,
            "get",
            return_value={"recording": mb_response},
        )
        mocker.patch.object(
            tasks.musicbrainz.api.recordings,
            "get",
            return_value={"recording": mb_response},
        )
        tasks.get_or_create_artists_credits_from_musicbrainz(
            mb_type, mb_response["id"], None, None
        )
        for i, ac in enumerate(mb_response["artist-credit"]):
            ac = models.ArtistCredit.objects.get(
                artist__name=ac["artist"]["name"],
                joinphrase=ac["joinphrase"],
                credit=ac["name"],
            )

            assert ac.artist.name == mb_response["artist-credit"][i]["artist"]["name"]
            assert (
                str(ac.artist.mbid) == mb_response["artist-credit"][i]["artist"]["id"]
            )
            assert ac.joinphrase == mb_response["artist-credit"][i]["joinphrase"]
