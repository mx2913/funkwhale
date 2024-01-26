import datetime
import logging
import re

# /!\ The next import have xml vulnerabilities but this shouldn't have security implication in funkwhale
# since there are only used to generate xspf file.
from xml.etree.ElementTree import Element, SubElement

from defusedxml import ElementTree as etree
from defusedxml import minidom
from django.core.exceptions import ObjectDoesNotExist

from funkwhale_api.music.models import Album, Artist, Track
from funkwhale_api.playlists.models import Playlist

logger = logging.getLogger(__name__)

# could use https://github.com/alastair/xspf/blob/master/xspf.py#L5 ?


def get_tracks_from_xspf(xspf):
    """
    Return a list of funkwhale tracks from xspf string. Tracks not found in database are ignored.
    """
    ns = "{http://xspf.org/ns/0/}"

    track_list = []
    tree = etree.fromstring(xspf)
    plt_name = tree.findtext(f"{ns}title")
    tracks = tree.findall(f".//{ns}track")
    added_track_count = 0

    for track in tracks:
        # Getting metadata of the xspf file
        try:
            artist = track.find(f".//{ns}creator").text
            title = track.find(f".//{ns}title").text
            album = track.find(f".//{ns}album").text
        except AttributeError as e:
            logger.info(
                f"Couldn't find the following attribute while parsing the xml file : {e!r}"
            )
            continue
        # Finding track id in the db
        try:
            artist_id = Artist.objects.get(name=artist)
            album_id = Album.objects.get(title=album)
        except Exception as e:
            logger.info(f"Error while querying database : {e!r}")
            continue
        try:
            fw_track = Track.objects.get(
                title=title, artist=artist_id.id, album=album_id.id
            )
        except ObjectDoesNotExist:
            try:
                fw_track = Track.objects.get(title=title, artist=artist_id.id)
            except ObjectDoesNotExist as e:
                logger.info(f"Couldn't find track in the database : {e!r}")
                continue
        if fw_track:
            track_list.append(fw_track)
            added_track_count = added_track_count + 1

    logger.info(
        str(len(tracks))
        + " tracks where found in xspf file. "
        + str(added_track_count)
        + " are gonna be added to playlist."
    )
    return track_list, plt_name


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
