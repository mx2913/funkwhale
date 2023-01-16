from defusedxml import ElementTree as etree

from funkwhale_api.playlists import models, utils


def test_get_tracks_from_xspf(factories):
    track1 = factories["music.Track"]()
    track2 = factories["music.Track"]()
    tracks_ids = [track1.id, track2.id]
    xspf_content = utils.generate_xspf_from_tracks_ids(tracks_ids)
    expected = ([track1, track2], "Test")
    assert utils.get_tracks_from_xspf(xspf_content) == expected


def test_generate_xspf_from_playlist(factories):
    playlist_track = factories["playlists.PlaylistTrack"]()
    playlist = playlist_track.playlist
    xspf_test = utils.generate_xspf_from_playlist(playlist.id)
    tree = etree.fromstring(xspf_test)
    # track1 = playlist_factory.playlist_tracks.get(id=1)
    # track1_name = track1.track
    track1_title = playlist_track.track.title
    # assert playlist.name == tree.findtext("./title")
    assert track1_title == tree.findtext("./trackList/track/title")
