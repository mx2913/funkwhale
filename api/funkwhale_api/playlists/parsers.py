import datetime
import decimal
import xml.etree.ElementTree as ET

from defusedxml import ElementTree as etree
from defusedxml.ElementTree import parse

from rest_framework.exceptions import ParseError
from rest_framework.parsers import BaseParser

from django.conf import settings

# stolen from https://github.com/jpadilla/django-rest-framework-xml/blob/master/rest_framework_xml/parsers.py

# class XSPFtoJSPF(BaseParser):


class XspfParser(BaseParser):
    """
    Takes a xspf sting, validated it, and return an xspf string
    """

    media_type = "application/octet-stream"

    def parse(self, stream, media_type=None, parser_context=None):
        # Avoid namespace prefixes, to do doesn't seems to work
        ET.register_namespace("", "http://xspf.org/ns/0/")

        try:
            tree = parse(stream, forbid_dtd=True)

        except (etree.ParseError, ValueError) as exc:
            raise ParseError("XML parse error - %s" % str(exc))
        if not tree.findtext("{http://xspf.org/ns/0/}title"):
            raise ParseError("Xspf must containt a Playlist tiltle")
        if not tree.findall(".//{http://xspf.org/ns/0/}track")[0]:
            raise ParseError("Xspf must containt a Playlist track")
        # to do check a title and a track list
        return ET.tostring(tree.getroot())
