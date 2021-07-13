import os

from defusedxml import ElementTree as etree

from funkwhale_api.playlists import models, utils


def test_get_track_id_from_xspf(factories, tmp_path):
    track1 = factories["music.Track"]()
    track2 = factories["music.Track"]()
    tracks_ids = [track1.id, track2.id]
    xspf_content = utils.generate_xspf_from_tracks_ids(tracks_ids)
    f = open("test.xspf", "w")
    f.write(xspf_content)
    f.close()
    xspf_file = "test.xspf"
    expected = [track1.id, track2.id]
    assert utils.get_track_id_from_xspf(xspf_file) == expected
    os.remove("test.xspf")


def test_generate_xspf_from_playlist(factories):
    playlist = factories["playlists.PlaylistTrack"]()
    xspf_test = utils.generate_xspf_from_playlist(playlist.id)
    tree = etree.fromstring(xspf_test)
    playlist_factory = models.Playlist.objects.get()
    track1 = playlist_factory.playlist_tracks.get(id=1)
    track1_name = track1.track
    assert playlist_factory.name == tree.findtext("./title")
    assert track1_name.title == tree.findtext("./trackList/track/title")
