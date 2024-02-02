import xml.etree.ElementTree as ElementTree

from defusedxml import ElementTree as etree
from defusedxml.ElementTree import parse

from rest_framework.exceptions import ParseError
from rest_framework.parsers import BaseParser

from django.conf import settings

# stolen from https://github.com/jpadilla/django-rest-framework-xml/blob/master/rest_framework_xml/parsers.py

# class XSPFtoJSPF(BaseParser):


class XspfParser(BaseParser):
    """
    Takes a xspf sting, validated it, and return an xspf json
    """

    media_type = "application/octet-stream"

    def parse(self, stream, media_type=None, parser_context=None):
        playlist = {"tracks": []}

        tree = parse(stream, forbid_dtd=True)
        root = tree.getroot()

        # Extract playlist information
        playlist_info = root.find(".")
        if playlist_info is not None:
            playlist["title"] = playlist_info.findtext(
                "{http://xspf.org/ns/0/}title", default=""
            )
            playlist["creator"] = playlist_info.findtext(
                "{http://xspf.org/ns/0/}creator", default=""
            )
            playlist["creation_date"] = playlist_info.findtext(
                "{http://xspf.org/ns/0/}date", default=""
            )
            playlist["version"] = playlist_info.attrib.get("version", "")

        # Extract track information
        for track in root.findall(".//{http://xspf.org/ns/0/}track"):
            track_info = {
                "location": track.findtext(
                    "{http://xspf.org/ns/0/}location", default=""
                ),
                "title": track.findtext("{http://xspf.org/ns/0/}title", default=""),
                "creator": track.findtext("{http://xspf.org/ns/0/}creator", default=""),
                "album": track.findtext("{http://xspf.org/ns/0/}album", default=""),
                "duration": track.findtext(
                    "{http://xspf.org/ns/0/}duration", default=""
                ),
            }
            playlist["tracks"].append(track_info)
        return playlist
