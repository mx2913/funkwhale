from rest_framework import renderers

from funkwhale_api.music.models import Album, Artist, Track
from funkwhale_api.playlists.models import Playlist

from xml.etree.ElementTree import Element, SubElement
import xml.etree.ElementTree as etree

from defusedxml import minidom


class PlaylistXspfRenderer(renderers.BaseRenderer):
    media_type = "application/octet-stream"
    format = "xspf"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if isinstance(data, bytes):
            return data

        fw_playlist = Playlist.objects.get(id=data["id"])
        plt_tracks = fw_playlist.playlist_tracks.prefetch_related("track")
        top = Element("playlist")
        top.set("version", "1")
        title_xspf = SubElement(top, "title")
        title_xspf.text = fw_playlist.name
        date_xspf = SubElement(top, "date")
        date_xspf.text = str(fw_playlist.creation_date)
        trackList_xspf = SubElement(top, "trackList")

        for plt_track in plt_tracks:
            track = plt_track.track
            write_xspf_track_data(track, trackList_xspf)
        return prettify(top)


def generate_xspf_from_playlist(playlist_id):
    """
    This returns a string containing playlist data in xspf format
    """
    fw_playlist = Playlist.objects.get(id=playlist_id)
    plt_tracks = fw_playlist.playlist_tracks.prefetch_related("track")
    top = Element("playlist")
    top.set("version", "1")
    title_xspf = SubElement(top, "title")
    title_xspf.text = fw_playlist.name
    date_xspf = SubElement(top, "date")
    date_xspf.text = str(fw_playlist.creation_date)
    trackList_xspf = SubElement(top, "trackList")

    for plt_track in plt_tracks:
        track = plt_track.track
        write_xspf_track_data(track, trackList_xspf)
    return prettify(top)


def write_xspf_track_data(track, trackList_xspf):
    """
    Insert a track into the trackList subelement of a xspf file
    """
    track_xspf = SubElement(trackList_xspf, "track")
    location_xspf = SubElement(track_xspf, "location")
    location_xspf.text = "https://" + track.domain_name + track.listen_url
    title_xspf = SubElement(track_xspf, "title")
    title_xspf.text = str(track.title)
    creator_xspf = SubElement(track_xspf, "creator")
    creator_xspf.text = str(track.artist)
    if str(track.album) == "[non-album tracks]":
        return
    else:
        album_xspf = SubElement(track_xspf, "album")
        album_xspf.text = str(track.album)


def prettify(elem):
    """
    Return a pretty-printed XML string for the Element.
    """
    rough_string = etree.tostring(elem, "utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
