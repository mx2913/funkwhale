from defusedxml import ElementTree as etree

from funkwhale_api.playlists import renderers, serializers


def test_generate_xspf_from_playlist(factories):
    playlist_track = factories["playlists.PlaylistTrack"]()
    playlist = playlist_track.playlist
    xspf_test = renderers.PlaylistXspfRenderer().render(
        serializers.PlaylistSerializer(playlist).data
    )
    tree = etree.fromstring(xspf_test)
    # track1 = playlist_factory.playlist_tracks.get(id=1)
    # track1_name = track1.track
    track1_title = playlist_track.track.title
    # assert playlist.name == tree.findtext("./title")
    assert track1_title == tree.findtext("./trackList/track/title")
