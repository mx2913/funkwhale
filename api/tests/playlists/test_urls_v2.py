import json

from defusedxml import ElementTree as etree

from django.urls import reverse
from django.shortcuts import resolve_url


def test_can_get_playlists_list(factories, logged_in_api_client):
    factories["playlists.Playlist"].create_batch(5)
    url = reverse("api:v2:playlists:playlists-list")
    headers = {"Content-Type": "application/json"}
    response = logged_in_api_client.get(url, headers=headers)
    data = json.loads(response.content)

    assert response.status_code == 200
    assert data["count"] == 5


def test_can_get_playlists_octet_stream(factories, logged_in_api_client):
    pl = factories["playlists.Playlist"]()
    factories["playlists.PlaylistTrack"](playlist=pl)
    factories["playlists.PlaylistTrack"](playlist=pl)
    factories["playlists.PlaylistTrack"](playlist=pl)

    url = reverse("api:v2:playlists:playlists-detail", kwargs={"pk": pl.pk})
    headers = {"Content-Type": "application/octet-stream"}
    response = logged_in_api_client.get(url, headers=headers)
    el = etree.fromstring(response.content)
    assert response.status_code == 200
    assert el.findtext("./title") == pl.name


def test_can_get_user_playlists_list(factories, logged_in_api_client):
    user = factories["users.User"]()
    factories["playlists.Playlist"](user=user)

    url = reverse("api:v2:playlists:playlists-list")
    url = resolve_url(url) + "?user=me"
    response = logged_in_api_client.get(url)
    data = json.loads(response.content.decode("utf-8"))

    assert response.status_code == 200
    assert data["count"] == 1


def test_can_post_user_playlists(factories, logged_in_api_client):
    playlist = {"name": "Les chiennes de l'hexagone", "privacy_level": "me"}
    url = reverse("api:v2:playlists:playlists-list")

    response = logged_in_api_client.post(url, playlist, format="json")
    data = json.loads(response.content.decode("utf-8"))
    assert response.status_code == 201
    assert data["name"] == "Les chiennes de l'hexagone"
    assert data["privacy_level"] == "me"


def test_can_post_playlists_octet_stream(factories, logged_in_api_client):
    artist = factories["music.Artist"](name="Davinhor")
    album = factories["music.Album"](title="Racisme en pls", artist=artist)
    factories["music.Track"](title="Opinel 12", artist=artist, album=album)
    url = reverse("api:v2:playlists:playlists-list")
    data = open("./tests/playlists/test.xspf", "rb").read()
    response = logged_in_api_client.post(url, data=data, format="xspf")
    data = json.loads(response.content)
    assert response.status_code == 201
    assert data["name"] == "Test"


def test_can_patch_playlists_octet_stream(factories, logged_in_api_client):
    pl = factories["playlists.Playlist"](user=logged_in_api_client.user)
    artist = factories["music.Artist"](name="Davinhor")
    album = factories["music.Album"](title="Racisme en pls", artist=artist)
    track = factories["music.Track"](title="Opinel 12", artist=artist, album=album)
    url = reverse("api:v2:playlists:playlists-detail", kwargs={"pk": pl.pk})
    data = open("./tests/playlists/test.xspf", "rb").read()
    response = logged_in_api_client.patch(url, data=data, format="xspf")
    pl.refresh_from_db()
    assert response.status_code == 201
    assert pl.name == "Test"
    assert pl.playlist_tracks.all()[0].track.title == track.title


def test_can_get_playlists_id(factories, logged_in_api_client):
    pl = factories["playlists.Playlist"]()
    url = reverse("api:v2:playlists:playlists-detail", kwargs={"pk": pl.pk})
    headers = {"Content-Type": "application/json"}

    response = logged_in_api_client.get(url, headers=headers, format="json")
    assert response.status_code == 200
    assert (
        etree.fromstring(response.content.decode("utf-8")).findtext("title") == pl.name
    )


def test_can_get_playlists_track(factories, logged_in_api_client):
    pl = factories["playlists.Playlist"]()
    plt = factories["playlists.PlaylistTrack"](playlist=pl)
    url = reverse("api:v2:playlists:playlists-tracks", kwargs={"pk": pl.pk})
    response = logged_in_api_client.get(url)
    data = json.loads(response.content.decode("utf-8"))
    assert response.status_code == 200
    assert data["count"] == 1
    assert data["results"][0]["track"]["title"] == plt.track.title


def test_can_get_playlists_releases(factories, logged_in_api_client):
    playlist = factories["playlists.Playlist"]()
    plt = factories["playlists.PlaylistTrack"](playlist=playlist)
    url = reverse("api:v2:playlists:playlists-releases", kwargs={"pk": playlist.pk})
    response = logged_in_api_client.get(url)
    data = json.loads(response.content)
    assert response.status_code == 200
    assert data[0]["title"] == plt.track.album.title


def test_can_get_playlists_artists(factories, logged_in_api_client):
    playlist = factories["playlists.Playlist"]()
    plt = factories["playlists.PlaylistTrack"](playlist=playlist)
    url = reverse("api:v2:playlists:playlists-artists", kwargs={"pk": playlist.pk})
    response = logged_in_api_client.get(url)
    data = json.loads(response.content)
    assert response.status_code == 200
    assert data[0]["name"] == plt.track.artist.name
