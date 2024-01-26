from defusedxml import ElementTree as etree

from funkwhale_api.playlists import utils


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
