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


def clean_namespace_xspf(xspf_file):
    """
    This will delete any namaespace found in the xspf file. It will also delete any encoding info.
    This way xspf file will be compatible with our get_track_id_from_xspf function.
    """
    file = open(xspf_file)
    with file as f:
        xspf_str = f.read()
    xspf_data = re.sub('xmlns="http://xspf.org/ns/0/"', "", xspf_str)
    # This is needed because lxml error : "ValueError: Unicode strings with encoding declaration are
    # not supported. Please use bytes input or XML fragments without declaration."
    xspf_data = re.sub("'encoding='.'", "", xspf_data)
    return xspf_data


def get_track_id_from_xspf(xspf_file):
    """
    Return a list of funkwhale tracks id from a xspf file. Tracks not found in database are ignored.
    """
    track_list = []
    xspf_data_clean = clean_namespace_xspf(xspf_file)
    tree = etree.fromstring(xspf_data_clean)
    tracks = tree.findall(".//track")
    added_track_count = 0

    for track in tracks:
        track_id = ""
        # Getting metadata of the xspf file
        try:
            artist = track.find(".//creator").text
            title = track.find(".//title").text
            album = track.find(".//album").text
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
            logger.info(f"Error while quering database : {e!r}")
        try:
            track_id = Track.objects.get(
                title=title, artist=artist_id.id, album=album_id.id
            )
        except ObjectDoesNotExist:
            try:
                track_id = Track.objects.get(title=title, artist=artist_id.id)
            except ObjectDoesNotExist as e:
                logger.info(f"Couldn't find track in the database : {e!r}")
        if track_id:
            track_list.append(track_id.id)
            added_track_count = added_track_count + 1

    logger.info(
        str(len(tracks))
        + " tracks where found in xspf file. "
        + str(added_track_count)
        + " are gonna be added to playlist."
    )
    return track_list


def generate_xspf_from_playlist(playlist_id):
    """
    This returns a string containing playlist data in xspf format
    """
    fw_playlist = Playlist.objects.get(id=playlist_id)
    plt_tracks = fw_playlist.playlist_tracks.prefetch_related("track")
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
        write_xspf_track_data(track, xpsf_tracklist)
    return prettify(xpsf_playlist)


def generate_xspf_from_tracks_ids(tracks_ids):
    """
    This returns a string containing playlist data in xspf format. It's used for test purposes.
    """
    xspf_title = "An automated generated playlist"
    now = datetime.now()
    xpsf_date = now.strftime("%m/%d/%Y")
    xpsf_playlist = Element("playlist")
    xpsf_tracklist = write_xpsf_headers(xpsf_playlist, xspf_title, xpsf_date)

    for track_id in tracks_ids:
        try:
            track = Track.objects.get(id=track_id)
            write_xspf_track_data(track, xpsf_tracklist)
        except ObjectDoesNotExist as e:
            logger.info(f"Error while quering database : {e!r}")
    return prettify(xpsf_playlist)


def write_xpsf_headers(xpsf_playlist, xpsf_title, xpsf_date):
    """
    This generate the playlist metadata and return a trackList subelement used to insert each track
    into the playlist
    """
    xpsf_playlist.set("version", "1")
    title_xspf = SubElement(xpsf_playlist, "title")
    title_xspf.text = xpsf_title
    date_xspf = SubElement(xpsf_playlist, "date")
    date_xspf.text = xpsf_date
    trackList_xspf = SubElement(xpsf_playlist, "trackList")
    return trackList_xspf


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
